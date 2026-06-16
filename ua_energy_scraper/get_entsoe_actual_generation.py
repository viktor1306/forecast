import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


GENERATION_URL = "https://transparency.entsoe.eu/generation/actual/perType/generation/load"
REQUEST_TIME_ZONE = "CET"

UA_AREAS = {
    "BZN|10Y1001C--00003F": "Ukraine bidding zone",
    "BZN|10Y1001C--000182": "UA-IPS bidding zone",
    "BZN|10Y1001A1001A869": "UA-DobTPP bidding zone",
    "CTY|10Y1001C--00003F": "Ukraine country",
    "SCA|10Y1001C--00003F": "Ukraine scheduling area",
    "SCA|10Y1001C--000182": "UA-IPS scheduling area",
    "SCA|10Y1001A1001A869": "UA-DobTPP scheduling area",
}

PRODUCTION_TYPES = {
    "B01": ("biomass_mw", "Biomass"),
    "B02": ("fossil_brown_coal_lignite_mw", "Fossil Brown coal/Lignite"),
    "B03": ("fossil_coal_derived_gas_mw", "Fossil Coal-derived gas"),
    "B04": ("fossil_gas_mw", "Fossil Gas"),
    "B05": ("fossil_hard_coal_mw", "Fossil Hard coal"),
    "B06": ("fossil_oil_mw", "Fossil Oil"),
    "B07": ("fossil_oil_shale_mw", "Fossil Oil shale"),
    "B08": ("fossil_peat_mw", "Fossil Peat"),
    "B09": ("geothermal_mw", "Geothermal"),
    "B10": ("hydro_pumped_storage_mw", "Hydro Pumped Storage"),
    "B11": ("hydro_run_of_river_mw", "Hydro Run-of-river and pondage"),
    "B12": ("hydro_water_reservoir_mw", "Hydro Water Reservoir"),
    "B13": ("marine_mw", "Marine"),
    "B14": ("nuclear_mw", "Nuclear"),
    "B15": ("other_renewable_mw", "Other renewable"),
    "B16": ("solar_mw", "Solar"),
    "B17": ("waste_mw", "Waste"),
    "B18": ("wind_offshore_mw", "Wind Offshore"),
    "B19": ("wind_onshore_mw", "Wind Onshore"),
    "B20": ("other_mw", "Other"),
    "B25": ("energy_storage_mw", "Energy storage"),
}

PRODUCTION_COLUMNS = [column for column, _ in PRODUCTION_TYPES.values()]
KYIV = ZoneInfo("Europe/Kyiv")
BRUSSELS = ZoneInfo("Europe/Brussels")


def parse_requested_date(value: str | None) -> date:
    if not value or value.lower() == "yesterday":
        return datetime.now(KYIV).date() - timedelta(days=1)
    if value.lower() == "today":
        return datetime.now(KYIV).date()
    try:
        return date.fromisoformat(value)
    except ValueError:
        pass
    try:
        day, month, year = value.split(".")
        return date(int(year), int(month), int(day))
    except (ValueError, AttributeError):
        raise argparse.ArgumentTypeError("Use YYYY-MM-DD, DD.MM.YYYY, today, or yesterday.")


def iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def entsoe_day_range(day: date) -> dict[str, str]:
    start = datetime(day.year, day.month, day.day, tzinfo=BRUSSELS)
    end = start + timedelta(days=1)
    return {"from": iso_z(start), "to": iso_z(end)}


def parse_iso(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def parse_duration(value: str) -> timedelta:
    match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?", value or "")
    if not match:
        raise ValueError(f"Unsupported ENTSO-E resolution: {value!r}")
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    return timedelta(hours=hours, minutes=minutes)


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://transparency.entsoe.eu",
            "Referer": "https://transparency.entsoe.eu/generation/actual/perType/generation",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
        },
    )
    try:
        with urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"HTTP {exc.code} from ENTSO-E: {detail}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"ENTSO-E request failed: {exc}") from exc


def fetch_generation(day: date, area_code: str) -> dict[str, Any]:
    payload = {
        "dateTimeRange": entsoe_day_range(day),
        "areaList": [area_code],
        "timeZone": REQUEST_TIME_ZONE,
        "sorterList": [],
        "filterMap": {},
    }
    return post_json(GENERATION_URL, payload)


def first_value(cells: Any) -> float | None:
    if not isinstance(cells, list):
        return None
    for cell in cells:
        if not isinstance(cell, dict) or "value" not in cell:
            continue
        value = cell["value"]
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    return None


def first_alt(cells: Any) -> str | None:
    if not isinstance(cells, list):
        return None
    for cell in cells:
        if isinstance(cell, dict) and cell.get("alt"):
            return str(cell["alt"])
    return None


def extract_rows(payload: dict[str, Any], day: date, area_code: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows_by_time: dict[datetime, dict[str, Any]] = {}
    alt_counter: Counter[str] = Counter()
    production_codes: set[str] = set()
    point_count = 0
    numeric_count = 0
    period_count = 0

    for instance in payload.get("instanceList", []):
        dimensions = instance.get("businessDimensionMap") or {}
        production_code = dimensions.get("PRODUCTION_TYPE", "UNKNOWN")
        production_codes.add(production_code)
        column_name = PRODUCTION_TYPES.get(production_code, (production_code.lower() + "_mw", production_code))[0]

        curve_data = instance.get("curveData") or {}
        for period in curve_data.get("periodList", []):
            period_count += 1
            start = parse_iso(period["timeInterval"]["from"])
            step = parse_duration(period.get("resolution", "PT60M"))
            point_map = period.get("pointMap") or {}
            for index_text, cells in point_map.items():
                point_count += 1
                value = first_value(cells)
                alt = first_alt(cells)
                if alt:
                    alt_counter[alt] += 1
                if value is None:
                    continue

                numeric_count += 1
                timestamp = start + int(index_text) * step
                row = rows_by_time.setdefault(
                    timestamp,
                    {
                        "date_requested": day.isoformat(),
                        "area_code": area_code,
                        "area_name": UA_AREAS.get(area_code, area_code),
                        "timestamp_utc": timestamp.isoformat().replace("+00:00", "Z"),
                        "timestamp_kyiv": timestamp.astimezone(KYIV).isoformat(),
                    },
                )
                row[column_name] = value

    rows = [rows_by_time[key] for key in sorted(rows_by_time)]
    stats = {
        "day": day.isoformat(),
        "area_code": area_code,
        "area_name": UA_AREAS.get(area_code, area_code),
        "instance_count": len(payload.get("instanceList", [])),
        "period_count": period_count,
        "point_count": point_count,
        "numeric_point_count": numeric_count,
        "production_codes": sorted(production_codes),
        "alt_counts": dict(sorted(alt_counter.items())),
    }
    return rows, stats


def write_csv(path: Path, rows: list[dict[str, Any]], production_columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = ["date_requested", "area_code", "area_name", "timestamp_utc", "timestamp_kyiv"] + production_columns
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def resolve_output_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return Path(__file__).resolve().parent / path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch Ukraine actual generation per production type from ENTSO-E Transparency Platform."
    )
    parser.add_argument(
        "--date",
        type=parse_requested_date,
        default=parse_requested_date("yesterday"),
        help="Date to request: YYYY-MM-DD, DD.MM.YYYY, today, or yesterday. Default: yesterday in Europe/Kyiv.",
    )
    parser.add_argument(
        "--scan-days",
        type=int,
        default=0,
        help="Also scan this many previous days and stop at the newest day that has numeric values.",
    )
    parser.add_argument(
        "--area",
        action="append",
        choices=sorted(UA_AREAS),
        help="ENTSO-E area code to query. Repeatable. Default: all known Ukraine area variants.",
    )
    parser.add_argument("--output", help="CSV output path. Relative paths are resolved inside ua_energy_scraper/.")
    parser.add_argument("--stats-output", help="Optional JSON path for per-query status diagnostics.")
    args = parser.parse_args()

    if args.scan_days < 0:
        parser.error("--scan-days must be zero or positive.")

    areas = args.area or list(UA_AREAS)
    stats_list: list[dict[str, Any]] = []
    all_rows: list[dict[str, Any]] = []
    found_day: date | None = None

    try:
        for offset in range(args.scan_days + 1):
            day = args.date - timedelta(days=offset)
            day_rows: list[dict[str, Any]] = []
            for area in areas:
                payload = fetch_generation(day, area)
                rows, stats = extract_rows(payload, day, area)
                stats_list.append(stats)
                day_rows.extend(rows)
                alt_summary = ", ".join(f"{key}={value}" for key, value in stats["alt_counts"].items()) or "none"
                print(
                    f"{day} {area}: instances={stats['instance_count']}, "
                    f"points={stats['point_count']}, numeric={stats['numeric_point_count']}, alt={alt_summary}"
                )
            if day_rows:
                all_rows.extend(day_rows)
                found_day = day
                break
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.stats_output:
        stats_path = resolve_output_path(args.stats_output)
        stats_path.parent.mkdir(parents=True, exist_ok=True)
        stats_path.write_text(json.dumps(stats_list, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote diagnostics to {stats_path}")

    if args.output:
        output_path = resolve_output_path(args.output)
        write_csv(output_path, all_rows, PRODUCTION_COLUMNS)
        print(f"Wrote {len(all_rows)} CSV rows to {output_path}")
    elif all_rows:
        writer = csv.DictWriter(
            sys.stdout,
            fieldnames=["date_requested", "area_code", "area_name", "timestamp_utc", "timestamp_kyiv"] + PRODUCTION_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(all_rows)

    if not all_rows:
        print(
            "No numeric actual generation values found. ENTSO-E returned metadata/curves, "
            "but the Ukraine points were empty or marked as n/e."
        )
        return 0

    print(f"Newest day with numeric generation values: {found_day}; rows={len(all_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
