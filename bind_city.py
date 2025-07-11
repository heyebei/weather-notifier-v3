import os
import json
import time
from weather_mailer import get_access_token, send_email

# 环境变量
from_user = os.environ['FROM_USER']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
tenant_id = os.environ['TENANT_ID']
recipients = os.environ['RECIPIENTS'].split(',')  # 逗号分隔

access_token = get_access_token(client_id, client_secret, tenant_id)

for recipient in recipients:
    content = "请直接回复此邮件，正文仅填写你想要接收天气信息的城市名（例如：Shanghai）"
    send_email(
        token=access_token,
        from_user=from_user,
        to_users=[recipient],
        subject="【绑定城市】请回复此邮件绑定你的城市",
        content=content
    )
    print(f"已发送绑定请求至 {recipient}")

