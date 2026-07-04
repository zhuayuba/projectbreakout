#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芒格计划 · 自动补货脚本

从某系列的最近一期 HTML 切下 JS 内核与 CSS 骨架，调 DeepSeek 生成新内容，
拼装成完整 HTML，做 ES5 合规校验后写入文件。

核心原则：JS 内核绝不让 AI 生成，原样复用最近一期的 <script>...</script>。

用法:
    python3 replenish.py <series> [--count N] [--dry-run] [--api-key KEY]
    series: stones | thinking | career
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

# ────────────────────────── 系列配置 ──────────────────────────

SERIES_CONFIG = {
    "stones": {
        "dir": "stones",
        "name_cn": "他山之石",
        "badge_prefix": "芒格计划 · 他山之石 · 第{N}期",
        "title_pattern": "第{N}期：{TITLE}",
        "lark_template": "blue",
        "prompt_file": "stones.txt",
    },
    "thinking": {
        "dir": "thinking",
        "name_cn": "另眼相看",
        "badge_prefix": "芒格计划 · 另眼相看 · 第{N}期",
        "title_pattern": "另眼相看 · 第{N}期：{TITLE}",
        "lark_template": "carmine",
        "prompt_file": "thinking.txt",
    },
    "career": {
        "dir": "career",
        "name_cn": "职人手艺",
        "badge_prefix": "芒格计划 · 职人手艺 · 第{N}期",
        "title_pattern": "职人手艺 · 第{N}期：{TITLE}",
        "lark_template": "blue",
        "prompt_file": "career.txt",
    },
}

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ────────────────────────── 日志 ──────────────────────────

class Log:
    def __init__(self, series):
        self.series = series
        self.entries = []

    def info(self, msg):
        line = "[{}] {}".format(self.series, msg)
        print(line, flush=True)
        self.entries.append(("info", msg))

    def warn(self, msg):
        line = "[{}][WARN] {}".format(self.series, msg)
        print(line, flush=True)
        self.entries.append(("warn", msg))

    def error(self, msg):
        line = "[{}][ERROR] {}".format(self.series, msg)
        print(line, flush=True)
        self.entries.append(("error", msg))

    def has_error(self):
        return any(lvl == "error" for lvl, _ in self.entries)


# ────────────────────────── HTML 切分 ──────────────────────────

def split_template(html_text):
    """把模板 HTML 切成三段: head(含style), body内容(供AI参考), script内核(原样复用).

    返回 dict:
      head:      <!DOCTYPE>...<body> 之前的全部 (含 <style>)
      script:    <script>...</script> 整段 (含标签)
      tail:      </body></html>
      body:      <body> 与 第一个 <script> 之间的内容 (供 AI 参考结构)
    """
    # head: 从开头到 <body> (含 <body> 行)
    body_start = html_text.find("<body>")
    if body_start < 0:
        raise ValueError("模板缺少 <body> 标签")
    head = html_text[:body_start + len("<body>")]

    # script 段: 最后一个 <script>...</script>
    script_start = html_text.rfind("<script>")
    script_end = html_text.find("</script>", script_start)
    if script_start < 0 or script_end < 0:
        raise ValueError("模板缺少 <script> 段")
    script = html_text[script_start:script_end + len("</script>")]

    # tail
    tail = html_text[script_end + len("</script>"):]

    # body 内容 (供 AI 参考结构, 不直接复用)
    body = html_text[body_start + len("<body>"):script_start]

    return {
        "head": head.strip() + "\n",
        "body": body.strip(),
        "script": script.strip() + "\n",
        "tail": tail.strip() + "\n",
    }


# ────────────────────────── ES5 合规校验 ──────────────────────────

FORBIDDEN_ES6 = [
    (r"\bconst\s", "const 声明"),
    (r"\blet\s", "let 声明"),
    (r"=>", "箭头函数 =>"),
]


def check_es5(html_text):
    """只扫描 <script>...</script> 区段是否含 ES6 语法. 返回 list[违规描述]."""
    violations = []
    # 提取所有 script 段
    for m in re.finditer(r"<script[^>]*>([\s\S]*?)</script>", html_text):
        code = m.group(1)
        for pat, desc in FORBIDDEN_ES6:
            if re.search(pat, code):
                violations.append(desc)
    return violations


# ────────────────────────── DeepSeek 调用 ──────────────────────────

def call_deepseek(prompt, api_key, timeout=120):
    """调 DeepSeek chat completions, 返回文本或 raise."""
    url = "https://api.deepseek.com/v1/chat/completions"
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是芒格计划的内容编辑。只输出 HTML 片段，不要任何解释文字、不要 markdown 代码块标记。"},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "max_tokens": 4000,
        "temperature": 0.8,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
    })
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        raise RuntimeError("DeepSeek API HTTP {}: {}".format(e.code, e.read().decode("utf-8", "ignore")[:200]))
    except Exception as e:
        raise RuntimeError("DeepSeek 调用失败: {}".format(e))


def strip_markdown_fence(text):
    """AI 可能不听话包了 ```html ... ```, 剥掉."""
    text = text.strip()
    if text.startswith("```"):
        # 去掉首行 ```html 或 ```
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


# ────────────────────────── 选题池 ──────────────────────────

def read_topics(pool_path, count):
    """读 topics_pool.md, 返回前 count 个候选选题 (字符串列表).

    格式: "11. 博弈论与囚徒困境——..." 这样的行.
    """
    if not os.path.exists(pool_path):
        return []
    with open(pool_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    topics = []
    for line in lines:
        s = line.strip()
        # 匹配 "数字. 内容" 格式的选题行
        m = re.match(r"^(\d+)\.\s*(.+)$", s)
        if m:
            topics.append(m.group(2).strip())
        if len(topics) >= count:
            break
    return topics


def remove_topics(pool_path, used_topics):
    """从 topics_pool.md 移除已用选题 (按内容匹配, 不依赖行号)."""
    if not os.path.exists(pool_path):
        return
    with open(pool_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    out = []
    for line in lines:
        s = line.strip()
        m = re.match(r"^(\d+)\.\s*(.+)$", s)
        if m:
            content = m.group(2).strip()
            # 检查这条选题是否已被用掉
            if any(content == u or content.startswith(u[:20]) for u in used_topics):
                continue  # 跳过已用
        out.append(line)
    with open(pool_path, "w", encoding="utf-8") as f:
        f.writelines(out)


# ────────────────────────── 库存计算 ──────────────────────────

def get_inventory(series_dir):
    """返回 (total_html, next_issue, reserve)."""
    htmls = [f for f in os.listdir(series_dir) if re.match(r"^\d{2}\.html$", f)]
    total = len(htmls)
    ni_path = os.path.join(series_dir, "next_issue.txt")
    next_issue = 1
    if os.path.exists(ni_path):
        with open(ni_path, "r", encoding="utf-8") as f:
            next_issue = int(f.read().strip() or "1")
    reserve = total - next_issue + 1
    return total, next_issue, reserve


def get_latest_html(series_dir):
    """返回该目录里期号最大的 NN.html 的完整路径."""
    htmls = [f for f in os.listdir(series_dir) if re.match(r"^\d{2}\.html$", f)]
    if not htmls:
        return None
    htmls.sort()
    return os.path.join(series_dir, htmls[-1])


# ────────────────────────── Prompt 构建 ──────────────────────────

def build_prompt(series, cfg, topic, issue_num, template_body):
    """读取 prompt 模板文件, 填入选题/期号/参考结构."""
    prompt_path = os.path.join(REPO_ROOT, "scripts", "prompts", cfg["prompt_file"])
    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.format(
        topic=topic,
        issue_num=issue_num,
        badge=cfg["badge_prefix"].format(N=issue_num),
        ref_structure=template_body,
    )


# ────────────────────────── 单期生成 ──────────────────────────

def generate_one(series, cfg, issue_num, topic, template_parts, api_key, log, dry_run):
    """生成一期 HTML. 返回生成的 HTML 文本, 或失败返回 None."""
    series_dir = os.path.join(REPO_ROOT, cfg["dir"])

    # 1. 构建 prompt
    try:
        prompt = build_prompt(series, cfg, topic, issue_num, template_parts["body"])
    except Exception as e:
        log.error("构建 prompt 失败: {}".format(e))
        return None

    if dry_run:
        log.info("[dry-run] 跳过 AI 调用, prompt 长度 {} 字符".format(len(prompt)))
        return None

    # 2. 调 DeepSeek
    log.info("调 DeepSeek 生成第 {} 期 (选题: {}...)".format(issue_num, topic[:30]))
    try:
        ai_content = call_deepseek(prompt, api_key)
    except Exception as e:
        log.error("AI 生成失败: {}".format(e))
        return None

    ai_content = strip_markdown_fence(ai_content)

    # 3. 基本校验: AI 输出不能含 <script> 或 <style>
    if "<script" in ai_content.lower():
        log.error("AI 输出含 <script> 标签, 拒绝采用 (防 JS 内核污染)")
        return None
    if "<style" in ai_content.lower():
        log.error("AI 输出含 <style> 标签, 拒绝采用 (CSS 应在 head 复用)")
        return None

    # 4. 拼装完整 HTML
    full_html = (
        template_parts["head"] + "\n"
        + ai_content + "\n"
        + template_parts["script"] + "\n"
        + template_parts["tail"]
    )

    # 5. ES5 合规校验 (只扫 script 段)
    violations = check_es5(full_html)
    if violations:
        log.error("ES5 合规校验失败, 发现: {}".format(", ".join(violations)))
        return None

    # 6. 关键字段校验 (Lark 抓取依赖)
    badge_check = cfg["badge_prefix"].format(N=issue_num)
    # badge 里期号必须是阿拉伯数字
    if str(issue_num) not in full_html:
        log.error("生成内容未包含期号 {}".format(issue_num))
        return None

    # 7. 写文件
    out_path = os.path.join(series_dir, "{:02d}.html".format(issue_num))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    log.info("✅ 第 {} 期已写入 {} ({} 字节)".format(issue_num, os.path.basename(out_path), len(full_html)))
    return full_html


# ────────────────────────── index.html 更新 ──────────────────────────

def update_index_career(series_dir, new_issues):
    """career/stones 的 index.html: 在最后一个 issue-card 后插入新卡片.

    thinking 的 index 太复杂 (学科分组 + disc-nav), 此函数不处理.
    """
    index_path = os.path.join(series_dir, "index.html")
    if not os.path.exists(index_path):
        return False
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    # 简化实现: 此处仅返回 True/False 表示是否需要手动更新
    # 完整的 index 更新逻辑较复杂, 留待 V2
    return False  # 初版: 都标记为需要手动更新, 发提醒


# ────────────────────────── 主流程 ──────────────────────────

def run_series(series, count, api_key, dry_run):
    cfg = SERIES_CONFIG[series]
    log = Log(cfg["name_cn"])
    series_dir = os.path.join(REPO_ROOT, cfg["dir"])

    if not os.path.isdir(series_dir):
        log.error("系列目录不存在: {}".format(series_dir))
        return log

    # 1. 库存检查
    total, next_issue, reserve = get_inventory(series_dir)
    log.info("库存: {} 期HTML, next_issue={}, 剩余 {} 期".format(total, next_issue, reserve))

    if reserve > 2:
        log.info("库存充足 (>2), 跳过补货")
        return log

    log.info("库存 ≤2, 触发补货")

    # 2. 读模板 (最近一期)
    latest = get_latest_html(series_dir)
    if not latest:
        log.error("找不到任何 HTML 模板")
        return log
    log.info("模板: {}".format(os.path.basename(latest)))
    with open(latest, "r", encoding="utf-8") as f:
        template_html = f.read()

    try:
        template_parts = split_template(template_html)
    except ValueError as e:
        log.error("切分模板失败: {}".format(e))
        return log

    # 3. 读选题
    pool_path = os.path.join(series_dir, "topics_pool.md")
    topics = read_topics(pool_path, count)
    if len(topics) < count:
        log.warn("选题池候选不足: 需 {}, 只有 {}".format(count, len(topics)))
    if not topics:
        log.error("选题池为空, 无法补货")
        return log
    log.info("取得 {} 个选题".format(len(topics)))

    # 4. 逐期生成
    generated = []
    used_topics = []
    for i, topic in enumerate(topics):
        issue_num = total + 1 + i  # 接着最大期号往后排
        result = generate_one(series, cfg, issue_num, topic, template_parts, api_key, log, dry_run)
        if result:
            generated.append(issue_num)
            used_topics.append(topic)
        else:
            log.warn("第 {} 期生成失败, 跳过".format(issue_num))
        # 礼貌限速, 避免触发 API rate limit
        if i < len(topics) - 1 and not dry_run:
            time.sleep(2)

    # 5. 移除已用选题
    if used_topics and not dry_run:
        remove_topics(pool_path, used_topics)
        log.info("已从 topics_pool 移除 {} 个已用选题".format(len(used_topics)))

    # 6. index 更新提示 (初版不自动改)
    if generated and not dry_run:
        log.warn("已生成 {} 期, 但 index.html 需手动更新卡片".format(len(generated)))

    log.info("完成: 成功生成 {} 期".format(len(generated)))
    return log


def main():
    parser = argparse.ArgumentParser(description="芒格计划自动补货")
    parser.add_argument("series", choices=list(SERIES_CONFIG.keys()), help="系列名")
    parser.add_argument("--count", type=int, default=6, help="生成几期 (默认6)")
    parser.add_argument("--dry-run", action="store_true", help="只检查库存和模板, 不调 API")
    parser.add_argument("--api-key", default=None, help="DeepSeek API key (默认读环境变量)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key and not args.dry_run:
        print("错误: 缺少 DeepSeek API key. 设环境变量 DEEPSEEK_API_KEY 或用 --api-key", file=sys.stderr)
        sys.exit(2)

    log = run_series(args.series, args.count, api_key, args.dry_run)
    sys.exit(1 if log.has_error() else 0)


if __name__ == "__main__":
    main()
