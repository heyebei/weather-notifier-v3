import os
import re
import time
import requests
import importlib.util
from bs4 import BeautifulSoup

from weather_mailer import get_access_token, send_email


def load_encrypt_funcs(path):
    """动态加载 `加密2.0.py`，并返回 encrypt, decrypt 两个可调用对象。"""
    spec = importlib.util.spec_from_file_location("encrypt_module", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # 期望模块中有 encrypt / decrypt 函数
    if not hasattr(mod, 'encrypt') or not hasattr(mod, 'decrypt'):
        raise RuntimeError(f"模块 {path} 中未发现 encrypt/decrypt 函数")
    return mod.encrypt, mod.decrypt


def get_inbox_messages(token, from_user, top=50):
    url = f'https://graph.microsoft.com/v1.0/users/{from_user}/mailFolders/Inbox/messages?$top={top}'
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json().get('value', [])


def mark_message_read(token, from_user, message_id):
    url = f'https://graph.microsoft.com/v1.0/users/{from_user}/messages/{message_id}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    resp = requests.patch(url, headers=headers, json={"isRead": True})
    resp.raise_for_status()


def extract_text_from_body(html_content: str) -> str:
    soup = BeautifulSoup(html_content or '', 'html.parser')
    if soup.body:
        return soup.body.get_text('\n', strip=True)
    return soup.get_text('\n', strip=True)


def parse_command(subject: str, body_text: str):
    """解析邮件，返回 (action, key, payload) 其中 action 为 'encrypt'|'decrypt' 或 None。"""
    subj = (subject or '').lower()
    body = body_text or ''

    # 优先通过主题判断操作
    if '加密' in subj or subj.startswith('enc:') or subj.startswith('encrypt'):
        action = 'encrypt'
    elif '解密' in subj or subj.startswith('dec:') or subj.startswith('decrypt'):
        action = 'decrypt'
    else:
        # 尝试在正文里查找明确命令
        if re.search(r'(^|\n)操作[:：]\s*加密', body):
            action = 'encrypt'
        elif re.search(r'(^|\n)操作[:：]\s*解密', body):
            action = 'decrypt'
        else:
            action = None

    # 提取密钥（支持：密钥: KEY 或 key: KEY）
    m = re.search(r'密钥[:：]\s*(\S+)', body) or re.search(r'key[:：]\s*(\S+)', body, re.I)
    key = m.group(1).strip() if m else None

    # 提取内容（优先查找 内容: 或 文本:，否则用整段正文）
    m2 = re.search(r'内容[:：]\s*([\s\S]+)', body)
    if m2:
        payload = m2.group(1).strip()
    else:
        # 若正文里有多行带标签的行（如 密钥: ...），移除这些后剩余的即为 payload
        payload = re.sub(r'(密钥[:：].*|key[:：].*|操作[:：].*)', '', body).strip()

    return action, key, payload


def process_messages(encrypt_fn, decrypt_fn, token, from_user, sender_whitelist=None):
    msgs = get_inbox_messages(token, from_user, top=50)
    for m in msgs:
        try:
            # 跳过已读的邮件
            if m.get('isRead'):
                continue

            sender = m.get('from', {}).get('emailAddress', {}).get('address')
            # 如果配置了白名单且发件人不在白名单，跳过（但标记为已读以避免重复）
            if sender_whitelist and sender not in sender_whitelist:
                print(f"跳过不在白名单的发件人: {sender}")
                mark_message_read(token, from_user, m.get('id'))
                continue
            subject = m.get('subject', '')
            body_html = m.get('body', {}).get('content', '')
            body_text = extract_text_from_body(body_html)

            action, key, payload = parse_command(subject, body_text)
            if not action:
                # 不相关的邮件，标记为已读并跳过
                mark_message_read(token, from_user, m.get('id'))
                continue

            if not key:
                reply = '未在邮件中找到密钥（请在正文中使用 "密钥: your_key"）。'
            elif not payload:
                reply = '未找到要处理的内容（请在正文中包含要加密/解密的文本，或使用 "内容: ..." 标注）。'
            else:
                try:
                    if action == 'encrypt':
                        result = encrypt_fn(payload, key)
                        reply = f'加密结果：\n{result}'
                    else:
                        result = decrypt_fn(payload, key)
                        reply = f'解密结果：\n{result}'
                except Exception as e:
                    reply = f'处理时发生错误：{e}'


            # 回复发件人
            if sender:
                send_email(token=token, from_user=from_user, to_users=[sender], subject=f'Re: {subject or "(无主题)"}', content=reply)

            # 标记为已读
            mark_message_read(token, from_user, m.get('id'))
            print(f"Processed message from {sender}, action={action}")
        except Exception as e:
            print(f"处理邮件 {m.get('id')} 时出错: {e}")


if __name__ == '__main__':
    # 环境变量
    from_user = os.environ.get('FROM_USER')
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    tenant_id = os.environ.get('TENANT_ID')

    if not all([from_user, client_id, client_secret, tenant_id]):
        raise SystemExit('缺少必要的环境变量：FROM_USER / CLIENT_ID / CLIENT_SECRET / TENANT_ID')

    # 加载加密模块（相对路径）
    encrypt_module_path = os.path.join(os.path.dirname(__file__), '加密2.0.py')
    if not os.path.exists(encrypt_module_path):
        raise SystemExit(f'找不到加密模块：{encrypt_module_path}')

    encrypt_fn, decrypt_fn = load_encrypt_funcs(encrypt_module_path)

    # 可配置的轮询间隔（秒）和 token 刷新间隔（秒）
    POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', '10'))
    TOKEN_REFRESH_INTERVAL = int(os.environ.get('TOKEN_REFRESH_INTERVAL', '1800'))

    # 可选的发件人白名单，逗号分隔
    whitelist_env = os.environ.get('SENDER_WHITELIST', '')
    sender_whitelist = set([s.strip() for s in whitelist_env.split(',') if s.strip()]) if whitelist_env else None

    print('开始持续监听收件箱以处理加密/解密请求...')

    token = None
    last_token_time = 0

    backoff = 1
    while True:
        try:
            # 在需要时刷新 token
            now = time.time()
            if not token or (now - last_token_time) > TOKEN_REFRESH_INTERVAL:
                token = get_access_token(client_id, client_secret, tenant_id)
                last_token_time = now

            process_messages(encrypt_fn, decrypt_fn, token, from_user, sender_whitelist=sender_whitelist)
            backoff = 1
        except Exception as e:
            print(f"运行时出错：{e}，{time.strftime('%Y-%m-%d %H:%M:%S')}")
            # 指数回退避免短时间内反复失败
            time.sleep(backoff)
            backoff = min(backoff * 2, 300)
        # 等待下一次轮询
        time.sleep(POLL_INTERVAL)
