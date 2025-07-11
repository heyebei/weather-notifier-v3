import os
import json
from weather_mailer import get_weather, get_access_token, send_email

from_user = os.environ['FROM_USER']
weather_api_key = os.environ['WEATHER_API_KEY']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
tenant_id = os.environ['TENANT_ID']

with open('email_city_map.json', 'r') as f:
    user_city_map = json.load(f)

access_token = get_access_token(client_id, client_secret, tenant_id)

for recipient, city in user_city_map.items():
    try:
        weather_info = get_weather(city, weather_api_key)
        send_email(
            token=access_token,
            from_user=from_user,
            to_users=[recipient],
            subject=f"{city} 今日天气播报",
            content=weather_info
        )
        print(f"✅ 已发送 {city} 天气给 {recipient}")
    except Exception as e:
        print(f"❌ 发送失败：{recipient} - {e}")
