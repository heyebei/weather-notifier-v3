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

    for mail in emails:
        sender = mail['from']['emailAddress']['address']
        city = mail.get('body', {}).get('content', '').strip().split()[0]
        if city and sender:
            mapping[sender] = city

    with open('email_city_map.json', 'w') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print("✅ 邮箱-城市映射已更新")

token = get_access_token()
emails = get_reply_emails(token)
update_mapping(emails)
