import requests

def get_weather(city: str, api_key: str) -> str:
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',
        'lang': 'zh_cn'
    }
    response = requests.get(url, params=params).json()
    if 'weather' not in response or 'main' not in response:
        # 这里可以记录 response，或者处理不同的错误码
        error_msg = response.get('message', '未知错误')
        raise ValueError(f"获取天气失败: {error_msg}")
    weather = response['weather'][0]['description']
    temp = response['main']['temp']
    return f"{city} 当前天气：{weather}，温度：{temp:.1f}°C"

def get_access_token(client_id, client_secret, tenant_id):
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        'client_id': client_id,
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    resp = requests.post(url, headers=headers, data=data)
    return resp.json()['access_token']

def send_email(token, from_user, to_users, subject, content):
    url = f'https://graph.microsoft.com/v1.0/users/{from_user}/sendMail'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": content
            },
            "toRecipients": [{"emailAddress": {"address": addr.strip()}} for addr in to_users]
        },
        "saveToSentItems": "true"
    }
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code >= 300:
        raise Exception(f"邮件发送失败: {resp.status_code} - {resp.text}")
