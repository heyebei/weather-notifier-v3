import os
import json
import requests
import time

def send_email():
    from weather_mailer import send_email, get_access_token, get_weather
    token = get_access_token(client_id, client_secret, tenant_id)
    for sender, city in new_bindings:
        weather_info = get_weather(city, os.environ['WEATHER_API_KEY'])
        send_email(token, from_user, [sender], f'{city} 天气通知', f"配置成功！\n\n{weather_info}")
    print("✅ 已向新用户发送天气确认邮件")
print("正在等待地址配置...")
time.sleep(300)
send_email()