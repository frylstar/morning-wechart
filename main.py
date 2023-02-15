from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random
from bs4 import BeautifulSoup

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

user_id = os.environ["USER_ID"]
user_id2 = os.environ["USER_ID2"]
template_id = os.environ["TEMPLATE_ID"]

hf_city_html = os.environ['HF_CITY_HTML']
hf_card_wrap = os.environ['HF_CARD_WRAP']
hr_card_abstract = os.environ['HF_CARD_ABSTRACT']


# def get_weather():
#   url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
#   res = requests.get(url).json()
#   weather = res['data']['list'][0]
#   return weather['weather'], math.floor(weather['temp']), math.floor(weather['low']), math.floor(weather['high'])

def get_weather_new():
  url = "https://devapi.qweather.com/v7/weather/now?location=101120901&key=bac728d865c64c07b592dc8466859894"
  response = requests.get(url).json()
  res = response['now']
  return res['text'], res['temp'], res['feelsLike'], res['windDir'], res['windScale'], res['precip'], res['humidity'], res['vis']

#2020-01-01
def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days + 1

#01-01
def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)

# 例如：今晚晴。明天小雨，温度和今天差不多（29°），空气不错。
def get_hf_weather_s():
  # url = 'https://www.qweather.com/weather/linyi-101120901.html'
  res = requests.get(hf_city_html)
  res.encoding='utf-8'
  html = res.text
  soup = BeautifulSoup(html, 'html.parser')
  # 天气卡片
  # card = soup.find('div', class_ = 'c-city-weather-current city-weather-sun')
  card = soup.find('div', class_ = hf_card_wrap)
  # 天气简要描述
  # detail = card.find('div', class_ = 'current-abstract')
  detail = card.find('div', class_ = hr_card_abstract)
  detail_str = detail.string
  return detail_str


client = WeChatClient(app_id, app_secret)

wm = WeChatMessage(client)
wea, temperature, feel_temp, wind_dir, wind_scale, precip, humidity, vis = get_weather_new()
data = {
  "city":{"value":city},
  "weather":{"value":wea},
  "temperature":{"value":temperature},
  "feel_temp": {"value":feel_temp}, # 体感温度
  "wind_dir": {"value":wind_dir},
  "wind_scale": {"value":wind_scale}, # 风力等级
  "precip": {"value":precip}, # 当前小时累计降水量 毫米
  "humidity": {"value":humidity}, # 相对湿度%
  "vis": {"value":vis}, # 能见度，公里
  "love_days":{"value":get_count()},
  "birthday_left":{"value":get_birthday()},
  "words":{"value":get_words(), "color":get_random_color()},
  "hf_abstract":{"value": get_hf_weather_s(), "color":get_random_color()}
}
res = wm.send_template(user_id, template_id, data)
wm.send_template(user_id2, template_id, data)
print(res)
