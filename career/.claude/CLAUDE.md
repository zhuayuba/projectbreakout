# 职人手艺 · Claude Code 速查卡

## 项目定位
每周两期（周三、周六晚8点），解剖一个具体职业的思维方式。大白话 + 生动案例。

## 网址与仓库
- 首页: `https://zhuayuba.github.io/mungerplan/career/`
- 第N期: `https://zhuayuba.github.io/mungerplan/career/NN.html`
- GitHub: `zhuayuba/mungerplan (career/ 子目录)`
- 本地: `/Users/linxiao/Desktop/project/data_radar/职人手艺/ (合并后: mungerplan/career/)`

## 文件结构
- `index.html` — 首页，每期一张卡片
- `NN.html` — 自包含 HTML（内容 + CSS + JS内核）
- `next_issue.txt` — 下期计数器
- `.github/workflows/weekly-push.yml` — 周三六 UTC 12:00 推送
- `agents.md` — 完整项目文档

## HTML 编写规范
- JS 必须用纯 ES5（`var`/`function`），不能有 `const`/`let`/箭头函数
- 第 2 行 `<span class="job-name">职业名</span>` 供 Lark 抓取
- 第 3 行 `<p class="hook">钩子</p>` 供 Lark 抓取
- 9 个模块结构：钩子 → 日常 → 新人踩坑 → 老手绝活 → 隐藏挑战 → 黄金技能 → 底层思维 → 跨界启发 → 总结预告
- 配色：主色 `#e8924c`（琥珀橙），Hero `#1a1d2e→#1a2744→#1a3856`
- 文案风格：口语化、案例驱动、2500-4000字

## 发布流程
1. 写 `NN.html`（含完整 JS 内核）
2. 更新 `index.html` 添加卡片
3. 更新 `next_issue.txt`
4. `git commit && git push`
5. GitHub Actions 自动在周三/六晚8点推送 Lark 卡片

## Lark 推送
- Webhook 和签名密钥存在 GitHub Secrets
- "职人手艺"是"芒格计划"旗下的子系列
- 与芒格计划共享同一个 Lark 群聊
- 推送时间互补：芒格计划周一、职人手艺周三+周六
