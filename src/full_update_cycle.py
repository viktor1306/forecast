import sys
import os
import logging
from datetime import datetime, timedelta

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from forecasting_core import ForecastingManager
from update_and_compare_v1 import main as compare_main

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_full_cycle():
    logger.info("🚀 Starting Full Update Cycle (12:45 Routine)")
    
    manager = ForecastingManager(base_dir=parent_dir)
    today = datetime.now()
    today_str = today.strftime("%d.%m.%Y")
    
    # 1. Update Weather (Today to +4 days)
    logger.info("🌤️ Updating Weather...")
    try:
        start_date = today_str
        end_date = (today + timedelta(days=4)).strftime("%d.%m.%Y")
        weather_data = manager.fetch_weather_data(start_date, end_date)
        if weather_data is not None:
             manager.update_weather_csv(weather_data)
             logger.info("✅ Weather updated.")
        else:
             logger.warning("⚠️ Failed to fetch weather.")
    except Exception as e:
        logger.error(f"❌ Error updating weather: {e}")

    # 2. Update RDN Data (Yesterday, Today, Tomorrow)
    dates_to_update = [
        today - timedelta(days=1), # Yesterday
        today,                     # Today
        today + timedelta(days=1)  # Tomorrow
    ]
    
    logger.info("📊 Updating RDN Data...")
    for dt in dates_to_update:
        d_str = dt.strftime("%d.%m.%Y")
        try:
            results = manager.fetch_oree_data(d_str, 'DAM')
            if results:
                manager.update_csv(results, d_str, 'DAM')
                logger.info(f"✅ RDN updated for {d_str}")
            else:
                logger.info(f"ℹ️ No RDN data for {d_str}")
        except Exception as e:
             logger.error(f"❌ Error updating RDN for {d_str}: {e}")

    # 3. Run Comparison for Today
    logger.info(f"📉 Running Comparison for {today_str}...")
    try:
        # We can call the main function of update_and_compare_v1
        # It expects argv or defaults to today. We can just call it with today_str argument simulation
        sys.argv = [sys.argv[0], today_str]
        compare_main()
        
        # Check if image was created
        output_img = os.path.join(parent_dir, "output", "comparison_latest.png")
        if os.path.exists(output_img):
            logger.info(f"✅ Comparison image generated: {output_img}")
            return True, output_img
        else:
            logger.warning("⚠️ Comparison image not found.")
            return False, None
            
    except Exception as e:
        logger.error(f"❌ Error running comparison: {e}")
        return False, None

if __name__ == "__main__":
    run_full_cycle()
