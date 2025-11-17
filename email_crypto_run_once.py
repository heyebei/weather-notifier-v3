import os
import sys
from weather_mailer import get_access_token
import importlib.util

from email_crypto_worker import load_encrypt_funcs, process_messages


def main():
    from_user = os.environ.get('FROM_USER')
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    tenant_id = os.environ.get('TENANT_ID')

    if not all([from_user, client_id, client_secret, tenant_id]):
        print('缺少环境变量 CLIENT_ID/CLIENT_SECRET/TENANT_ID/FROM_USER')
        sys.exit(1)

    # 加载加密模块
    encrypt_module_path = os.path.join(os.path.dirname(__file__), '加密2.0.py')
    if not os.path.exists(encrypt_module_path):
        print(f'找不到加密模块：{encrypt_module_path}')
        sys.exit(1)

    encrypt_fn, decrypt_fn = load_encrypt_funcs(encrypt_module_path)

    token = get_access_token(client_id, client_secret, tenant_id)

    whitelist_env = os.environ.get('SENDER_WHITELIST', '')
    sender_whitelist = set([s.strip() for s in whitelist_env.split(',') if s.strip()]) if whitelist_env else None

    # 调用 email_crypto_worker 中的 process_messages 一次性执行并退出
    process_messages(encrypt_fn, decrypt_fn, token, from_user, sender_whitelist=sender_whitelist)


if __name__ == '__main__':
    main()
