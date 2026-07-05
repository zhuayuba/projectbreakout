# AGENTS.md — 破茧计划（projectbreakout monorepo）

> 本文件是整个仓库的总协调文档。三个系列各自的内容规范、JS 内核、配色等细节，由对应子目录下的 `agents.md` 承担，本文不重复——只在你需要快速定位"去哪儿看"时指路。

## 这是什么

一套**跨学科思维模型的内容自动推送系统**，灵感来自查理·芒格的"格栅理论"。把各学科最核心的思维模型，做成精美的自包含 HTML 阅读卡片，定时推送到飞书群。

三个系列**互补不重复**，构成格栅的横线与纵线，外加一条职业落地线：

| 系列 | 子目录 | 定位 | 做法一句话 |
|------|--------|------|-----------|
| 📐 他山之石 | `stones/` | 跨学科思维模型（硬科学） | 从各学科**提取**模型，横着用 |
| 🧠 另眼相看 | `thinking/` | 学科底层思维习惯 | **钻进**一个学科，竖着学它的思考方式 |
| 🔧 职人手艺 | `career/` | 具体职业的思维方式 | 解剖一个**职业**的内功心法 |

读者入口：`https://zhuayuba.github.io/projectbreakout/`（根 `index.html` 是三系列总览）。

## 仓库结构

```
projectbreakout/                          ← 本仓库 (zhuayuba/mungerplan)
├── index.html                       ← 三系列总入口页
├── .nojekyll                        ← 确保 Pages 正确发布子目录
├── .github/workflows/
│   ├── push-stones.yml              ← 他山之石 定时推送
│   ├── push-thinking.yml            ← 另眼相看 定时推送
│   └── push-career.yml              ← 职人手艺 定时推送
├── stones/                          ← 他山之石（详见 stones/agents.md）
│   ├── 01.html ~ 10.html
│   ├── index.html, next_issue.txt, topics_pool.md, agents.md, 开发日志.md
├── thinking/                        ← 另眼相看（详见 thinking/agents.md）
│   ├── 01.html ~ 04.html
│   ├── index.html, next_issue.txt, topics_pool.md, agents.md, 部署日志.md
└── career/                          ← 职人手艺（详见 career/agents.md）
    ├── 01.html ~ 10.html
    ├── index.html, next_issue.txt, topics_pool.md, agents.md, series-design.md
```

各子目录的 `agents.md` 是该系列的权威规范（内容模板、JS 内核、配色、HTML 结构等），改动系列内容前必读。

## 三个系列的关键差异（速查）

| 维度 | stones 他山之石 | thinking 另眼相看 | career 职人手艺 |
|------|----------------|------------------|----------------|
| 推送时间（北京） | 周一、周四 20:00 | 周二、周五 20:00 | 周三、周六 20:00 |
| cron（UTC 12:00） | `0 12 * * 1,4` | `0 12 * * 2,5` | `0 12 * * 3,6` |
| workflow 文件 | `push-stones.yml` | `push-thinking.yml` | `push-career.yml` |
| 飞书卡片色 | blue | carmine | blue |
| 当前期号（next_issue） | 5 | 3 | 3 |
| 已有期数 | 10 | 4 | 10 |
| 标题抓取字段 | `.model` + `h3` | `h1` + `.meta` + `.sub` | `.job-name` + `.hook` |
| 配色基调 | 深海军蓝 + 金色（冷调） | 深酒红 + 暖铜（暖调） | 琥珀橙 + 深蓝 hero |
| localStorage 前缀 | `munger_backup` | `munger_thinking_*` | `munger_career_*`（按系列隔离） |
| Pages URL | `…/projectbreakout/stones/NN.html` | `…/projectbreakout/thinking/NN.html` | `…/projectbreakout/career/NN.html` |

> 三个系列错峰推送，周一到周六每天晚上 20:00 都有一期，周日休。

## 通用技术约束（三个系列共同）

这些是**所有 HTML 文件共享的硬性约束**，无论改哪个系列都要遵守：

1. **完全自包含** — 每个 `.html` 内联 CSS + HTML + JS，无 npm / CDN / 外部脚本。双击即可在 `file://` 打开。
2. **纯 ES5** — 只用 `var` / `function`，**严禁** `const` / `let` / 箭头函数 / 模板字符串。原因：`file://` 协议下 ES6+ 会静默失败，无任何报错。
3. **JS 内核逐字复制** — 各系列最近一期里的 `<script>` 内核是"成品"，生成新期时整体复制，**一个字都不改**。
4. **期号必须用阿拉伯数字** — `.hero-badge` / 标题区里的"第 X 期"必须写阿拉伯数字，否则 `info()` 解析返回 0，标记数据无法入库。
5. **localStorage 按系列隔离** — 三个系列用不同前缀（见上表），防止数据互相污染。

## 推送机制（仓库级）

### 双层自动化

```
┌─────────────────────────────────────────────────────────────┐
│ 第一层：GitHub Actions（远端，负责定时推送飞书）              │
│   每到对应 cron → checkout → cd 子目录 → 抓标题 → 发飞书      │
│   → 计数器+1 commit → 库存≤2 则发预警                        │
├─────────────────────────────────────────────────────────────┤
│ 第二层：本地 scheduled_task（每周日 03:57，负责自动补货）      │
│   扫三个系列库存 → 若 ≤2 则从 topics_pool 取 6 选题生成 6 期  │
│   → 更新 index.html → commit + push                          │
└─────────────────────────────────────────────────────────────┘
```

### 一个 workflow 改了什么（以 push-career.yml 为例）

合并 monorepo 时，三个 workflow 都做了同样的两处关键改造：

1. **`defaults.run.working-directory: ./career`** — 让"确定本期号/推送 Lark/库存预警"这些步骤默认在子目录执行，能直接 `cat next_issue.txt`、`ls [0-9][0-9].html`。
2. **"计数器+1"步骤里 `cd $GITHUB_WORKSPACE`** — 因为 `git add`/`git commit`/`git push` 必须在仓库根执行，且 `git add career/next_issue.txt` 要用仓库根的相对路径。
3. **URL 前缀加子目录** — `https://zhuayuba.github.io/projectbreakout/career/${FILE}.html`。

修改 workflow 时这三点必须保留。

### 必须配置的 Secrets 与权限

在 `zhuayuba/projectbreakout` → Settings 里：

| 位置 | 配置项 | 作用 |
|------|--------|------|
| Secrets and variables → Actions | `LARK_WEBHOOK_URL` | 飞书机器人 webhook |
| Secrets and variables → Actions | `LARK_SIGNING_SECRET` | 飞书签名密钥 |
| Actions → General → Workflow permissions | **Read and write** | 让 schedule 触发的 token 能 push `next_issue.txt`（不配会导致计数器步骤 403） |

三个系列**共享同一对 secrets**（推到同一个飞书群）。签名算法：HMAC-SHA256(key=`timestamp\nsecret`, data="") → Base64。

### 本地定时补货任务

- 配置：`data_radar/.claude/scheduled_tasks.json`，cron `57 3 * * 0`（每周日 03:57）
- 操作目标：本仓库 `projectbreakout/` 工作区
- 逻辑：对每个系列算 `库存 = 已有 HTML 数 - next_issue + 1`；库存 ≤ 2 时从对应 `topics_pool.md` 取前 6 个选题，生成 6 期新 HTML + 更新 index.html + commit/push，并把用过的选题从池中移除
- **git 操作必须在仓库根执行**，commit message 前缀标明系列（如「他山之石 → 补货 #11-16」）

## 本地工作区

```
data_radar/
├── projectbreakout/                    ← 本仓库的工作区（所有 git 操作在这里）
├── 他山之石/  另眼相看/  职人手艺/  ← 合并前的旧目录，保留作备份，勿再修改
└── .claude/scheduled_tasks.json   ← 本地定时补货任务
```

日常开发、补货、提交都在 `projectbreakout/` 里进行。三个旧目录是合并前的历史快照，仅作回滚备份用途。

## 常见任务指引

### 发布新一期（手动）

1. 在对应子目录以 `01.html` 为模板创建 `NN.html`（**不要从前一期复制**，前一期可能已偏离模板）
2. 完整复制该系列 JS 内核，一字不改
3. 更新该子目录 `index.html`（加卡片 / 把 future 改成已发布）
4. 更新 `next_issue.txt`？—— **不要手动改**。推送 workflow 会自动 +1。手动改会导致和 Actions 的自增冲突。
5. 在 `projectbreakout/` 根目录 `git add 对应子目录 && git commit && git push`

### 修改推送时间 / 改飞书卡片样式

改对应子目录的 `push-*.yml`。注意三处必保留：`working-directory`、`cd $GITHUB_WORKSPACE`、URL 子路径前缀。

### 新增第四个系列

1. 建子目录（英文短名），放入 `index.html` / `01.html…` / `next_issue.txt`（写 1）/ `topics_pool.md` / 子目录 `agents.md`
2. 在根 `.github/workflows/` 加 `push-xxx.yml`（复制现有任意一个改：name / cron / working-directory / URL / 标题抓取正则 / 卡片色）
3. 根 `index.html` 加一张导航卡片
4. 更新本文件的"三个系列"表格（变四个）
5. 更新 `data_radar/.claude/scheduled_tasks.json` 把新子目录加入补货扫描清单

## 已知坑（合并后务必留意）

1. **GitHub Actions schedule 不可靠** — 高峰期常延迟 30 分钟～2 小时，且新 workflow 首次定时触发经常被跳过。建议新 workflow 上线后先手动 `workflow_dispatch` 触发一次验证。
2. **schedule 触发的 token 默认只读** — 必须在 Settings 里开 Workflow permissions 为 read+write，否则"计数器+1"push 失败（历史 bug，已通过 workflow 里 `permissions: contents: write` + 仓库设置双保险）。
3. **子目录相对链接** — 各子目录 HTML 内部链接是相对路径（`01.html`），整体搬动子目录不会断；但跨系列链接（如 `thinking/index.html` 里的 `../stones/index.html`）依赖子目录名，**改名子目录要同步改这些链接**。
4. **Pages 首次部署可能超时** — 新内容 push 后如果 Pages 卡在 `deployment_queued`，去 Settings → Pages 把 Branch 切到 None 再切回 main / root，通常第三次成功。

## 旧仓库（归档）

合并前另有 `zhuayuba/mungerplan-thinking` 和 `zhuayuba/career-lab` 两个独立仓库，现已并入本仓库的 `thinking/` 和 `career/`。旧仓库保留作历史归档，旧链接（`…/mungerplan-thinking/`、`…/career-lab/`）不再维护，读者应访问 `…/projectbreakout/thinking/` 和 `…/projectbreakout/career/`。
