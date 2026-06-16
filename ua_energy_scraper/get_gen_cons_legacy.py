import http.client
import json
import pandas as pd


def get_gen_con(dateforecast):
  dateforecast = pd.to_datetime(dateforecast).date()
  year = dateforecast.year
  month = dateforecast.month
  day = dateforecast.day
  if len(str(day)) == 1:
    day = "0" + str(day)
  if len(str(month)) == 1:
    month = "0" + str(month)
  conn = http.client.HTTPSConnection("ua.energy")
  payload = "action=get_data_oes_only&report_date="+str(day)+"."+str(month)+"."+str(year)+"&type=day&rnd=0.9018575009491707"
  headers = {
    'authority': 'ua.energy',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'accept': '*/*',
    'x-requested-with': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://ua.energy',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://ua.energy/peredacha-i-dyspetcheryzatsiya/dyspetcherska-informatsiya/dobovyj-grafik-vyrobnytstva-spozhyvannya-e-e/',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6'}
  conn.request("POST", "/wp-admin/admin-ajax.php", payload, headers)
  tt=conn.getresponse().read().decode("utf-8")
  data = pd.DataFrame(json.loads(conn.getresponse().read().decode("utf-8")))
  data.drop(data.tail(1).index, inplace=True)
  data['hour'] = pd.to_datetime(str(dateforecast) + ' ' + data['hour'])
  data.rename(columns={'hour': 'DateTime'}, inplace=True)
  return(data)

print(get_gen_con("2026-03-01"))
