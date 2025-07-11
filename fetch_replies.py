import os
import json
import requests

from_user = os.environ['FROM_USER']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
tenant_id = os.environ['TENANT_ID']

def get_access_token():
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        'client_id': client_id,
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(url, headers=headers, data=data)
    return r.json()['access_token']

def get_reply_emails(token):
    url = f'https://graph.microsoft.com/v1.0/users/{from_user}/mailFolders/Inbox/messages?$top=20'
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers)
    return r.json()['value']

def update_mapping(emails):
    try:
        with open('email_city_map.json', 'r') as f:
            mapping = json.load(f)
    except:
        mapping = {}

    new_bindings = []
    for mail in emails:
        sender = mail['from']['emailAddress']['address']
        city = mail.get('body', {}).get('content', '').strip().split()[0]
        if city and sender and (sender not in mapping):
            mapping[sender] = city
            new_bindings.append((sender, city))

    with open('email_city_map.json', 'w') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print("✅ 邮箱-城市映射已更新")

    # 发送确认邮件
    if new_bindings:
        from weather_mailer import send_email, get_access_token, get_weather
        token = get_access_token(client_id, client_secret, tenant_id)
        for sender, city in new_bindings:
            weather_info = get_weather(city, os.environ['WEATHER_API_KEY'])
            send_email(token, from_user, [sender], f'{city} 天气通知', f"配置成功！\n\n{weather_info}")
        print("✅ 已向新用户发送天气确认邮件")

token = get_access_token()
emails = get_reply_emails(token)
update_mapping(emails)
