# 🌤️ Weather Notifier v2（支持自动绑定）

该项目支持：
- 给多个邮箱发送不同城市天气
- 首次自动发送绑定请求
- 用户回复后自动记录邮箱-城市映射
- 后续每天发送对应城市天气

## 📦 使用说明

1. 设置以下环境变量（GitHub Secrets 或本地 `.env`）

| 名称             | 说明                       |
|------------------|----------------------------|
| CLIENT_ID        | Azure 应用的 client_id     |
| CLIENT_SECRET    | 应用密钥                   |
| TENANT_ID        | Azure 租户 ID              |
| FROM_USER        | 发件邮箱（必须为组织用户） |
| WEATHER_API_KEY  | OpenWeatherMap 的 API Key  |
| RECIPIENTS       | 初始绑定的邮箱（逗号分隔） |

2. 第一步运行绑定命令

```bash
python bind_city.py
```

3. 第二步运行检查回复并提取城市

```bash
python fetch_replies.py
```

4. 第三步每天运行天气发送脚本

```bash
python send_weather.py
```

你也可以将其整合进 GitHub Actions 或定时器中运行。
