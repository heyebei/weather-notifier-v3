import os
import importlib.util
import sys
import pathlib

import pytest

# 将仓库根目录加入路径（以便相对导入）
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from email_crypto_worker import parse_command


def load_encrypt_module():
    path = ROOT / '加密2.0.py'
    spec = importlib.util.spec_from_file_location('encrypt_mod', str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_parse_subject_encrypt():
    subject = '加密'
    body = '密钥: k123\n内容: hello world'
    action, key, payload = parse_command(subject, body)
    assert action == 'encrypt'
    assert key == 'k123'
    assert payload == 'hello world'


def test_parse_body_operation():
    subject = ''
    body = '操作: 解密\n密钥: s3cr3t\n内容: YWJj'
    action, key, payload = parse_command(subject, body)
    assert action == 'decrypt'
    assert key == 's3cr3t'
    assert payload == 'YWJj'


def test_encrypt_decrypt_roundtrip():
    mod = load_encrypt_module()
    assert hasattr(mod, 'encrypt') and hasattr(mod, 'decrypt')
    plaintext = '这是一个测试文本'
    key = 'mykey'
    enc = mod.encrypt(plaintext, key)
    dec = mod.decrypt(enc, key)
    assert dec == plaintext
