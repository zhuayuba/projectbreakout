# 职人手艺 —— 项目文档

## 概述

每周两期（周三、周六晚8点），解剖一个具体职业，挖出从业者的思维方式、黄金技能和外人看不到的挑战。用大白话写，配生动案例。

## 网址

- 首页：`https://zhuayuba.github.io/projectbreakout/career/`
- 第 N 期：`https://zhuayuba.github.io/projectbreakout/career/NN.html`（如 `01.html`）

## 代码仓库

- GitHub：`zhuayuba/projectbreakout (career/ 子目录)`
- 本地路径：`/Users/linxiao/Desktop/project/data_radar/职人手艺/ (合并后: projectbreakout/career/)`
- 文件格式：每期一个自包含 HTML 文件（`01.html` ~ `NN.html`），首页 `index.html`
- JS 内核：纯 ES5（`var`/`function`，无 `const`/`let`/箭头函数），内嵌在 HTML 中

## 每期 HTML 结构

```html
<span class="job-name">职业名称（用于 Lark 推送抓取）</span>
<p class="hook">一句话钩子（用于 Lark 推送抓取）</p>
```

内容结构（9 个模块）：
1. 开篇钩子
2. 一天的真实面貌
3. 新人崩溃时刻
4. 老手的肌肉记忆
5. 外人看不到的挑战
6. 黄金技能 Top 3
7. 底层思维模型
8. 跨界启发
9. 一句话总结 + 下期预告

## Lark 推送

- Webhook URL：存入 GitHub Secret `LARK_WEBHOOK_URL`
- 签名密钥：存入 GitHub Secret `LARK_SIGNING_SECRET`
- 推送时间：周三和周六 UTC 12:00（北京时间 20:00）
- cron：`0 12 * * 3,6`
- 消息格式：Lark 交互卡片，蓝色标题栏

## 自动化机制

- GitHub Actions 工作流：`.github/workflows/weekly-push.yml`
- 计数器文件：`next_issue.txt`
- 流程：读取 `next_issue.txt` → 推送交互卡片 → 计数器 +1 → 提交
- 也可通过 `workflow_dispatch` 手动触发

## 如何发布新一期

1. 创建 `NN.html`（如 `11.html`），包含完整 JS 内核
2. 更新 `index.html`，添加新卡片
3. `git commit && git push`
4. 计数器会自动处理推送

## 视觉标识

- 主色调：琥珀橙 `#e8924c`
- Hero 渐变：`#1a1d2e → #1a2744 → #1a3856`
- 卡片底色：`#faf8f5`
- 字体：正文 Georgia/Noto Serif SC，UI PingFang SC

## 与破茧计划的关系

- "职人手艺"是"破茧计划"旗下的子系列
- 同一套技术架构（自包含 HTML + GitHub Pages + Lark 推送）
- 独立的 GitHub 仓库和域名路径
- 共享 Lark Webhook（推送到同一个群聊）
- 发布节奏互补：破茧计划周一、职人手艺周三+周六
