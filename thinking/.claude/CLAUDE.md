# 芒格计划·思维模式篇 — Claude Code 速查

## 项目定位

芒格计划的姊妹系列。"学科季"模式——像物理学家、经济学家、历史学家一样思考，大白话讲透每个学科的底层思维。

- **芒格计划**：跨学科提取模型，横着用（训练触类旁通）
- **思维模式篇**：深入单一学科，竖着学（训练换位思考）
- **两者互补不重复**

## 技术硬约束

- 纯静态 HTML，自包含（CSS + HTML + JS 全在一个文件）
- JS **必须 ES5**：`var`/`function`，禁用 `const`/`let`/`=>`/模板字符串/`async`
- `file://` 协议兼容
- 无外部依赖（no npm, CDN, external fonts/scripts）

## 配色（与芒格计划刻意不同）

| 元素 | 值 |
|---|---|
| Hero 渐变 | `#2d1320 → #1f0d18 → #140810`（深酒红） |
| 强调色 | `#c97a5a`（暖铜） |
| 高亮盒 | `#faf3f0 → #f5e4d8`（暖粉调） |

## 文件命名

- `index.html` — 目录索引
- `NN.html` — 各期内容（连续编号 01-48，共 12 学科 × 4 期）
- `next_issue.txt` — 推送计数器

## 单期模板（6 段结构）

🔬 学科视角 → 💎 一句话记住 → 🌙 晚间引子 → 🏛️ 生活应用（details） → 🔄 反过来想 → 🧠 给你的启示

## JS 内核

每期必须逐字复制完整 JS 内核（~9KB），包含：
- 右键标记/笔记（`mh`, `mc` class）
- 右下笔记本侧边栏（`fab` id）
- 左下 AI 助教（`_aipn`），DeepSeek API
- localStorage 前缀：`munger_thinking_*`（与芒格计划 `munger_*` 隔离）

## 创建新期次

1. 以 `01.html` 为模板
2. 改 hero 内容 + `--disc-color` 为对应学科色
3. 改 hero `::after` 光晕色
4. 复制 JS 内核，**一个字不改**
5. 更新 `index.html` 卡片状态
6. 更新前后期的底部学科导航

## 底部导航

每期底部有学科导航芯片（12 学科）+ 季内期次跳转。同一学科内期次互相链接，当前期高亮。

## 部署

- 仓库：`zhuayuba/mungerplan (thinking/ 子目录)`
- Pages：`https://zhuayuba.github.io/mungerplan/thinking/`
- Lark 推送：每周二、四 UTC 12:00（北京 20:00），cron: `0 12 * * 2,4`
- Secrets：`LARK_WEBHOOK_URL`、`LARK_SIGNING_SECRET`

## 已知坑

1. **新建 GitHub 仓库不要勾"Add README"** → 会导致 push 冲突
2. **git 身份必须配置**：`user.name` + `user.email`
3. **Pages 部署卡队列**：Settings → Pages → Branch 切 None → 再切回 main
4. **Workflow 计数器写失败**：需要 `permissions: contents: write`
5. **配色别用深蓝/深绿**：和芒格计划太像，用深酒红
6. **localStorage key 前缀**：`munger_thinking_*`，不能和芒格计划 `munger_*` 混用

## 当前进度

- ✅ S1 物理学（01-04）
- ⬜ S2-S12 待创建
- `next_issue.txt` 当前值见文件
