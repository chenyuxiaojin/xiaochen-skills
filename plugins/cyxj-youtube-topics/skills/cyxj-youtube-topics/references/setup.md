# 前置准备：环境变量与依赖（首次使用 / 报缺 key 时读）

配一次永久生效。已经跑通过的机器不需要读本文件；只有首次配置、换机器、
或脚本报 `YOUTUBE_API_KEY`/`APIFY_API_TOKEN` 缺失、403 quotaExceeded 时才回来看。

`${SKILL_DIR}` = `${CLAUDE_PLUGIN_ROOT}/skills/cyxj-youtube-topics`

---

1. **YouTube Data API v3 Key**（必需，可配多个轮询）
   - 在 https://console.cloud.google.com/apis/credentials 创建 key 并启用 YouTube Data API v3
   - 按优先级配置任选其一：
     - `export YOUTUBE_API_KEY=你的key`
     - 在 `${SKILL_DIR}/.env` 写入 `YOUTUBE_API_KEY=你的key`
     - 在 `~/.config/cyxj/.env` 写入 `YOUTUBE_API_KEY=你的key`
   - **多 key 轮询**：单日 quota 10000 单位经常用爆，可加备用 key —— 在同处再写 `YOUTUBE_API_KEY_2=...`、`YOUTUBE_API_KEY_3=...`。脚本 403 quotaExceeded 时自动切下一个 key 重试。⚠️ 备用 key 必须来自**不同的 Google Cloud 项目**才有独立配额，同项目里加几个 key 也是同一份 quota。变量名大小写不敏感、`_2` 和 `2` 都认。

2. **Obsidian 选题库目录**（必需）
   - `export CYXJ_TOPIC_DIR="$HOME/obsidian/灵感库/选题库"`

3. **用户个人档案**（可选，但强烈建议）
   - `export CYXJ_USER_PROFILE="$HOME/obsidian/.../个人档案.md"`
   - 内容应包含：身份定位、内容聚焦方向、目标受众、不做什么、代表作品
   - 有这个文件，判断层能给"差异化切口"建议；没有时降级为客观判断

4. **Apify API Token**（必需，字幕抓取主路径）
   - 注册 apify.com，Settings → API & Integrations → Personal API Token
   - 主路径 Actor：`scrape-creators/best-youtube-transcripts-scraper`（脚本直接按 Actor ID 调用，无需 bookmark）
   - 按优先级配置任选其一：
     - `export APIFY_API_TOKEN=你的token`
     - 在 `${SKILL_DIR}/.env` 写入 `APIFY_API_TOKEN=你的token`
     - 在 `~/.config/cyxj/.env` 写入 `APIFY_API_TOKEN=你的token`
   - Free plan 每月 $5 credit，scrape-creators 约 $0.001/条，每月 600 视频约 $0.6，远在 Free 额度内

5. **Supadata API Key**（可选，fallback 兜底）
   - 注册 supadata.ai，dashboard 拷贝 API key
   - 配置：同 Apify，变量名 `SUPADATA_API_KEY`
   - Free tier 每月 100 credits，应急 fallback 够用
   - 不配置也能跑，只是主路径挂时没兜底（Supadata 是独立服务商、独立 IP 池，与 Apify 不共享额度）

6. **Python 依赖**：`pip install -r requirements.txt`
   - 必需：`requests`
   - 不再需要 `youtube-transcript-api`（主路径已换 Apify 代理，不走 YouTube 内部接口）

## 高级环境变量（可选，从脚本实际行为归纳）

- `CYXJ_STATE_DIR`：覆盖状态目录（话题索引 / 创作者索引 / 判断日志 / `.seen_video_ids.json` 的存放处；默认 `~/Library/Application Support/cyxj-youtube-topics/state`，为避 iCloud 文件锁不放同步目录）
- `CYXJ_TRUSTED_BACKEND`：信任频道直查后端，`youtube_api`（默认）或 `apify`（测试用，不烧 YouTube quota，且会跳过关键词召回）
- `CYXJ_LOOKBACK_HOURS`：召回回看窗口小时数，默认 48，取值范围 1–168
- `CYXJ_PHASE`：两段式 cron 专用；`=1` 时 `write_topics.py` 硬锁拒绝写盘（防廉价模型越界），`=2` 或不设则放行
