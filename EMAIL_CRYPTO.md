# 自动加解密工作流说明

此文件说明如何使用 `email_crypto_worker.py`：当配置的发件邮箱收到带“加密/解密”指令的邮件时，会自动调用仓库中的 `加密2.0.py` 的算法进行处理并回复发件人。

快速开始：

1. 设置环境变量（在运行环境中设置）：

   - CLIENT_ID
   - CLIENT_SECRET
   - TENANT_ID
   - FROM_USER

2. 发送测试邮件给 `FROM_USER`，示例正文格式：

```
操作: 加密
密钥: mysecret
内容: 这是要加密的明文
```

或在主题中写明 `加密` 或 `解密`，正文中包含 `密钥:` 和要处理的文本。

3. 运行脚本：

```
python email_crypto_worker.py
```

注意事项：

- 当前实现为一次性轮询并处理未读邮件并将其标记为已读，适合轻量使用。
- 推荐在生产中使用 Microsoft Graph webhook 或将脚本加入稳定的调度（如 cron、系统服务或云函数）。
- `加密2.0.py` 中必须包含 `encrypt(msg, key)` 与 `decrypt(msg, key)` 两个函数，脚本会动态加载并调用。
