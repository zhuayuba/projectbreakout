#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书告警发送脚本 - 供 auto-replenish workflow 调用.

用法: python3 notify_lark.py "告警标题" "告警内容(可含换行)"
依赖环境变量: LARK_WEBHOOK_URL, LARK_SIGNING_SECRET
"""

import hashlib
import hmac
import base64
import json
import os
import sys
import time
import urllib.request


def send(title, content, template="red"):
    webhook = os.environ.get("LARK_WEBHOOK_URL", "")
    secret = os.environ.get("LARK_SIGNING_SECRET", "")
    if not webhook or not secret:
        print("缺少 LARK_WEBHOOK_URL 或 LARK_SIGNING_SECRET, 跳过告警", file=sys.stderr)
        return False

    ts = str(int(time.time()))
    sign_string = ts + "\n" + secret
    sign = base64.b64encode(
        hmac.new(sign_string.encode("utf-8"), b"", hashlib.sha256).digest()
    ).decode("utf-8")

    body = json.dumps({
        "timestamp": ts,
        "sign": sign,
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": template,
            },
            "elements": [
                {"tag": "markdown", "content": content}
            ],
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        webhook,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req, timeout=15)
    print(resp.read().decode("utf-8"))
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: notify_lark.py <标题> <内容>", file=sys.stderr)
        sys.exit(2)
    title = sys.argv[1]
    content = sys.argv[2]
    ok = send(title, content)
    sys.exit(0 if ok else 1)
