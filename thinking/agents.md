# AGENTS.md — 另眼相看（芒格计划）

## 项目概述

另眼相看是芒格计划的姊妹系列。核心思路：**用"学科季"模式，像物理学家、经济学家、历史学家……一样思考**。每季聚焦一个学科，每季 4 期，每期讲透该学科的一种底层思维习惯。目标是用大白话说清楚"像XX家一样思考"到底意味着什么。

### 与芒格计划的关系

| | 芒格计划 | 另眼相看 |
|---|---|---|
| 做法 | 从各学科**提取**思维模型，横着用 | **进入**一个学科，竖着学它的思考方式 |
| 内容 | 熵增、相变、网络效应等跨学科模型 | "历史学家怎么想？""社会学家怎么看？" |
| 结构 | 每期一个模型 | 每学科一季（4 期），每期一种底层思维 |
| 配色 | 深海军蓝 + 金色（`#c8a45c`） | 深酒红 + 暖铜（`#c97a5a`） |
| 推送 | 每周一 UTC 12:00 | 每周二、四 UTC 12:00 |
| 仓库 | `zhuayuba/mungerplan` | `zhuayuba/mungerplan (thinking/ 子目录)` |
| Lark 卡片色 | blue | carmine |

两个系列**互补不重复**：芒格计划是格栅的横线，另眼相看是格栅的纵线。

## 文件结构

```
芒格计划-思维模式篇/
├── index.html           ← 目录索引页（12学科 × 4期 = 48张卡片，按学科分组）
├── 01.html ~ 04.html    ← 物理学第1季（已发布，4期完整）
├── 05.html ~ 08.html    ← 生物学第2季（待创建）
├── ...                  ← 后续学科待创建
├── next_issue.txt       ← 推送计数器（当前值：2）
├── agents.md            ← 本文件
├── 部署日志.md           ← 部署踩坑记录
├── .github/workflows/
│   └── weekly-push.yml  ← Lark 每周推送工作流
├── .nojekyll            ← 告诉 GitHub Pages 不启用 Jekyll
└── .gitignore
```

## 技术约束（极其重要）

### 1. 完全自包含
- 每个 `.html` 文件包含 **CSS + HTML + JS**，不依赖任何外部资源
- 无 npm、无 CDN、无外部样式表、无外部脚本
- 通过 `file://` 协议也可直接打开

### 2. 纯 ES5 JavaScript（硬性约束）
- **只能使用 `var` 和 `function`**，严禁 `const`、`let`、`=>`、模板字符串、`async/await`
- 所有字符串使用双引号 `"`
- JS 包裹在 IIFE 中：`(function(){"use strict"; ... })();`
- **原因**：`file://` 协议下 ES6+ 语法可能静默失败

### 3. localStorage 隔离

为避免两个系列的数据互相污染，另眼相看使用独立前缀：
- 标记数据：`munger_thinking_backup`
- AI 密钥：`munger_thinking_ai_key`
- AI 对话：`munger_thinking_ai_chat`
- AI 上下文缓存：`munger_thinking_ai_context`

芒格计划使用 `munger_*` 前缀，两者完全隔离。

## 每期内容模板

每期 HTML 文件遵循固定结构，但与芒格计划不同——重点不是"硬科学模型"，而是**学科底层思维习惯**：

1. **hero** — 学科色光晕（deep wine + discipline accent）
   - `.hero-badge`：必须包含阿拉伯数字 "另眼相看 · 第X期"
   - `.hero-tags`：学科名称 + 期号/总期数
   - `h1` + `.sub` + `.meta`
2. **intro-card** — 引言卡片，建立阅读期待
3. **🔬 学科视角** — 这个学科怎么看世界？物理学家/历史学家/社会学家的核心本能是什么
4. **💎 一句话记住它** — 放在 `.highlight-box` 中
5. **🌙 晚间引子** — 大白话问题引发思考，串联学科思维和日常生活
6. **🏛️ 生活中的应用** — 2-3 个可折叠 `<details>` 面板，用学科思维重新解读日常现象
7. **🔄 反过来想** — 逆向思考题（芒格核心方法论），放在特殊配色的 `.highlight-box` 中
8. **🧠 给你的启示** — 对个人决策的具体启发
9. **底部学科导航** — 12学科 chips + 季内期次跳转

### HTML 常用元素

```
header.hero          ← 深酒红 hero banner（`#2d1320 → #140810`）
  .hero-badge        ← 必须包含阿拉伯数字
  .hero-tags>span    ← 学科标签
div.container
  div.intro>.intro-card  ← 引言卡片
  section            ← 主体内容
    h3               ← 章节标题
    details>summary  ← 可折叠面板（+ / − 圆形切换按钮，颜色用学科色）
    blockquote       ← 学科金句（左边框用学科色，暖灰背景）
    .highlight-box   ← 高亮提示框（暖粉调背景 `#faf3f0`）
    .disc-nav        ← 底部学科导航网格
```

## 配色方案

### 页面主色（与芒格计划刻意区分）

| 元素 | 颜色 | 用途 |
|---|---|---|
| Hero 渐变 | `#2d1320 → #1f0d18 → #140810` | 深酒红背景 |
| 强调色 | `#c97a5a` | hero 图标文字、链接、按钮角标 |
| 强调色暗 | `#9a5040` | hover 状态 |
| 高亮盒背景 | `#faf3f0 → #f5e4d8` | 暖粉调 |
| 高亮盒边框 | `#d8c0b0` | |
| 高亮盒文字 | `#5a3030` | |
| 反向思考盒背景 | `#faf3f0 → #f0e0d8` | 比高亮盒稍深 |
| 反向思考盒边框 | `#d0b8b0` | |
| 页脚链接 | `#c97a5a` | |

### 学科强调色（12 个学科）

每季有独立的学科色，用于期号背景、blockquote 左边框、details 切换按钮：

| 学科 | 颜色 | 色值 |
|---|---|---|
| 物理学 | 蓝 | `#4a7fb5` |
| 生物学 | 绿 | `#3a8a5c` |
| 化学 | 橄榄绿 | `#7b8a4a` |
| 心理学 | 紫 | `#8a5c9e` |
| 经济学 | 橙 | `#c07a3a` |
| 历史学 | 玫瑰红 | `#b56576` |
| 社会学 | 青 | `#5b8c85` |
| 数学 | 蓝绿 | `#4a8a9a` |
| 哲学 | 深紫 | `#6a5a8a` |
| 工程学 | 灰蓝 | `#5a7a8a` |
| 计算机科学 | 海蓝 | `#3a6a8a` |
| 统计学 | 灰紫 | `#7b6b8a` |

**配色历史**：
- 最初用了深蓝+金色（和芒格计划太像）
- 改成深林绿+古铜（差别还是不够大）
- 最终定为**深酒红+暖铜**（暖调 vs 芒格的冷调，一眼区分）

## JS 内核规范

### 功能模块

JS 内核在每个期文件中约 9KB，包含：

- **右键标记** — 选中文本 → 右键 → "⭐ 标记" / "📝 记笔记"
- **高亮恢复** — 页面加载时从 localStorage 恢复本期所有标记
- **标记气泡** — 点击高亮文本弹出笔记内容和操作按钮（添加笔记/删除）
- **侧边栏笔记本** — 右下角 "📒 笔记本" 浮动按钮 → 右侧滑出面板
- **AI 助教** — 左下角 "🤖 AI 助教" 浮动按钮 → 左侧滑出面板（DeepSeek API）
- **Toast 通知** — 轻量操作反馈

### 关键变量

- 数据数组：`_h`（内存主存储）
- 高亮元素 class：`mh`
- 侧边栏卡片 class：`mc`
- 浮动按钮 id：`fab`
- 标记计数器 id：`bdg`
- AI 面板元素：`_aipn`、`_aiov`

### 关键函数

- `info()` — 解析 `.hero-badge` 中的期号（支持阿拉伯和中文数字）
- `addHl(tx, nt)` — 添加高亮标记
- `delHl(id)` — 删除高亮标记
- `updHl(id, nt)` — 更新高亮笔记
- `act(note)` — 工具栏动作分发
- `restore()` — 从 localStorage 恢复本期标记
- `mkSide()` / `tog()` / `renderSB()` — 笔记本侧边栏
- `mkAIPanel()` / `togAI()` — AI 助教侧边栏
- `ensureContext(cb)` — 通过 XHR 读取所有已发布 HTML 构建 AI 上下文
- `callDeepSeek(msgs, cb)` — 调用 DeepSeek API
- `toast(msg)` — 显示 toast 通知

### AI 上下文自动同步

AI 助教启动时通过 XHR 拉取所有已发布期次的 HTML 文件，提取标题、学科标签和正文摘要（前 2000 字），构建 system prompt。`total` 变量控制读取范围，当前设 `total=4`（仅物理学），新学科上线后需更新此值。

## 创建新期次的步骤

1. 确定期号（如 `05`）、所属学科、底层思维名称
2. 以 `01.html` 为模板创建 `XX.html`
3. 修改 hero 内容（期号、标题、副标题、meta）
4. 替换 CSS 中的 `--disc-color` 为对应学科色
5. 修改 hero `::after` 光晕颜色为对应学科色
6. 填入六段内容（学科视角、一句话金句、晚间引子、生活应用、反过来想、启示）
7. 更新底部学科导航：`disc-nav-season` 中当前期号标为 `active`
8. **完整复制 JS 内核**（不能有任何修改）
9. 更新 `index.html`：该期卡片从 `issue-card-future` 改为 `issue-card`，状态从"待发布"改为"已发布"
10. 更新前一期和后一期的底部学科导航（启用链接/更新 active 位置）

## GitHub Pages 部署

### 仓库信息
- **仓库**：`zhuayuba/mungerplan (thinking/ 子目录)`
- **URL**：`https://zhuayuba.github.io/mungerplan/thinking/`
- **分支**：`main`
- **Pages source**：GitHub Actions（通过 `.github/workflows/deploy-pages.yml`）

### 踩坑记录

#### 坑 1：仓库初始化冲突
**现象**：创建仓库时勾选 "Add a README file" → 本地 push 时报 `failed to push some refs`。

**原因**：远程 README 和本地代码历史不相关，产生冲突。

**解决**：删除仓库重建，**三个初始化选项全部不勾**（不要 README、不要 .gitignore、不要 license）。

#### 坑 2：Git 身份未配置
**现象**：`Author identity unknown` → commit 失败。

**解决**：
```bash
git config --global user.name "zhuayuba"
git config --global user.email "你的GitHub邮箱"
```

#### 坑 3：GitHub Pages 部署超时
**现象**：Actions 中 `pages build and deployment` 一直显示 `deployment_queued`，最终超时红叉（`Timeout reached, aborting!`）。

**原因**：GitHub Pages 部署队列偶发卡死，新仓库首次部署时概率较高。

**尝试过的无效方案**：
- 添加 `.nojekyll` 文件
- Re-run failed jobs

**有效方案**：
1. Settings → Pages → Branch 改为 **None** → Save
2. 再改回 **main / (root)** → Save
3. 触发新部署，通常第三次成功

#### 坑 4：Workflow 计数器推送失败（exit code 128）
**现象**：Lark 卡片推送成功，但最后一步 `git push` 报 `403 Permission denied`。

**原因**：GitHub Actions 默认只有仓库读取权限，不能写 `next_issue.txt`。

**解决**：在 workflow 文件中添加：
```yaml
permissions:
  contents: write
```

#### 坑 5：配色与芒格计划太像
**现象**：最初使用深蓝 hero + gold accent → 和芒格计划几乎一样。换成深绿 → 差别仍然不够大。

**解决**：换深酒红 `#2d1320` + 暖铜 `#c97a5a`（暖调 vs 冷调，视觉差异明显）。

## Lark 推送配置

### 工作流：`.github/workflows/weekly-push.yml`

- **推送节奏**：每周二、四 UTC 12:00（北京时间 20:00）
- **cron**：`0 12 * * 2,4`
- **计数器**：`next_issue.txt`（自动递增）
- **也可手动触发**：`workflow_dispatch`，可指定期号

### Lark 卡片格式

- `msg_type`：`interactive`（交互卡片）
- `template`：`carmine`（红色标题栏）
- 内容：期号 + 思维名称 + 副标题 + 学科标签 + "📖 开始阅读 →" 按钮
- 按钮链接到 `https://zhuayuba.github.io/mungerplan/thinking/NN.html`

### 所需 Secrets

| Secret 名 | 内容 |
|---|---|
| `LARK_WEBHOOK_URL` | Lark 自定义机器人 Webhook 地址（`open.larksuite.com`） |
| `LARK_SIGNING_SECRET` | Lark 签名校验密钥 |

### 签名算法

HMAC-SHA256(key=`timestamp\nsecret`, data="") → Base64

### 推送规则

- 计数器从 1 开始，每推送一期自动 +1
- 手动触发不指定期号时，推送计数器当前值并递增
- 手动触发指定期号时，推送指定期，不影响计数器

## 学科规划（12 学科 × 4 期 = 48 期）

| 季 | 学科 | 期号 | 状态 |
|---|---|---|---|
| S1 | 物理学 | 01-04 | ✅ 已发布 |
| S2 | 生物学 | 05-08 | ⬜ 待创建 |
| S3 | 化学 | 09-12 | ⬜ 待创建 |
| S4 | 心理学 | 13-16 | ⬜ 待创建 |
| S5 | 经济学 | 17-20 | ⬜ 待创建 |
| S6 | 历史学 | 21-24 | ⬜ 待创建 |
| S7 | 社会学 | 25-28 | ⬜ 待创建 |
| S8 | 数学 | 29-32 | ⬜ 待创建 |
| S9 | 哲学 | 33-36 | ⬜ 待创建 |
| S10 | 工程学 | 37-40 | ⬜ 待创建 |
| S11 | 计算机科学 | 41-44 | ⬜ 待创建 |
| S12 | 统计学 | 45-48 | ⬜ 待创建 |
