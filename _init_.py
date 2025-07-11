import os
import json
import requests
import time
from_user = os.environ['FROM_USER']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
tenant_id = os.environ['TENANT_ID']
def send_email():
    from weather_mailer import send_email, get_access_token, get_weather
    token = get_access_token(client_id, client_secret, tenant_id)
    for sender, city in new_bindings:
        weather_info = get_weather(city, os.environ['WEATHER_API_KEY'])
        send_email(token, from_user, [sender], f'{city} 天气通知', f"配置成功！\n\n{weather_info}")
    print("✅ 已向新用户发送天气确认邮件")
print("正在等待地址配置...")

send_email()