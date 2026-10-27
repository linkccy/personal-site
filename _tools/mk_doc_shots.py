"""把三份 Markdown 文档渲染成「文档截图」，用于第七天实训的 04 题（需求文档 / 技术文档 / AGENTS.md）。

做法：用 markdown 库把指定行范围的片段转成 HTML ->
套一层 VS Code 深色主题的样式 -> 无头 Chrome + CDP 截整页图。

用法：python _tools/mk_doc_shots.py
"""
import base64
import json
import os
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request

import markdown
import websocket
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(os.path.dirname(ROOT), "第七天提交截图")
TMP = os.path.join(os.environ.get("TEMP", "."), "docshots")
CDP_PORT = 9254
PROFILE = os.path.join(os.environ.get("TEMP", "."), "cdp_doc_profile")

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

WIDTH = 1500
DSF = 2

CSS = """
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #1e1e1e; }
body { font-family: "Microsoft YaHei", "Segoe UI", system-ui, sans-serif; }
.win { width: __W__px; background: #252526; }
.bar { height: 44px; background: #2d2d30; display: flex; align-items: center;
       gap: 9px; padding: 0 16px; border-bottom: 1px solid #3c3c3c; }
.dot { width: 12px; height: 12px; border-radius: 50%; flex: 0 0 auto; }
.r { background: #ff5f57; } .y { background: #febc2e; } .g { background: #28c840; }
.tab { margin-left: 14px; background: #1e1e1e; color: #d4d4d4; font-size: 12.5px;
       padding: 5px 14px; border-radius: 6px 6px 0 0; border: 1px solid #3c3c3c;
       border-bottom: none; font-family: Consolas, "Cascadia Mono", monospace; }
.badge { margin-left: auto; font-size: 12.5px; color: #8b8b8b; }
.doc { padding: 26px 46px 36px; }
h1 { font-size: 27px; color: #ffffff; margin: 0 0 18px; padding-bottom: 12px;
     border-bottom: 1px solid #3c3c3c; font-weight: 700; }
h2 { font-size: 20px; color: #4ec9b0; margin: 28px 0 12px; font-weight: 700; }
h3 { font-size: 16.5px; color: #569cd6; margin: 22px 0 9px; font-weight: 700; }
h4 { font-size: 15px; color: #c586c0; margin: 18px 0 8px; }
p, li, dd, dt { font-size: 14.5px; line-height: 1.8; color: #cfcfcf; }
p { margin: 10px 0; }
ul, ol { margin: 10px 0; padding-left: 24px; }
li { margin: 4px 0; }
li > ul, li > ol { margin: 4px 0; }
code { background: #2d2d30; color: #ce9178; padding: 1px 5px; border-radius: 4px;
       font-family: Consolas, "Cascadia Mono", monospace; font-size: 13.5px; }
pre { background: #1b1b1c; border: 1px solid #3c3c3c; border-radius: 6px;
      padding: 13px 15px; margin: 12px 0; }
pre code { background: none; color: #d4d4d4; padding: 0; font-size: 13.3px; line-height: 1.6; }
table { border-collapse: collapse; width: 100%; margin: 13px 0; font-size: 13.8px; }
th { background: #2d2d30; color: #ffffff; text-align: left; font-weight: 600; }
th, td { border: 1px solid #3c3c3c; padding: 7px 11px; color: #cfcfcf; vertical-align: top;
         line-height: 1.65; }
strong { color: #ffffff; }
em { color: #dcdcaa; font-style: normal; }
blockquote { border-left: 3px solid #4ec9b0; margin: 12px 0; padding: 2px 0 2px 15px;
             color: #a8b0bb; background: #2a2a2b; border-radius: 0 6px 6px 0; }
blockquote p { color: #a8b0bb; margin: 6px 0; }
hr { border: none; border-top: 1px solid #3c3c3c; margin: 24px 0; }
a { color: #4fc1ff; text-decoration: none; }
"""

# (输出文件名, 源文件, 起始行, 结束行, 徽标文字)
BANDS = [
    ("04-文档-1-PRD-背景与目标.png", "PRD.md", 1, 36,
     "PRD.md · 产品需求文档 · 第 1–36 行 / 共 283 行"),
    ("04-文档-2-PRD-功能需求.png", "PRD.md", 73, 113,
     "PRD.md · 功能需求 FR-1 / FR-2 · 第 73–113 行"),
    ("04-文档-3-PRD-验收与个性化差异.png", "PRD.md", 244, 275,
     "PRD.md · 验收标准 + 与示例的差异 · 第 244–275 行"),

    ("04-文档-4-技术设计-选型与理由.png", "TECH_DESIGN.md", 1, 51,
     "TECH_DESIGN.md · 技术栈选型与理由 · 第 1–51 行 / 共 281 行"),
    ("04-文档-5-技术设计-结构与数据模型.png", "TECH_DESIGN.md", 52, 130,
     "TECH_DESIGN.md · 项目结构 + 数据模型 · 第 52–130 行"),
    ("04-文档-6-技术设计-关键技术点.png", "TECH_DESIGN.md", 155, 205,
     "TECH_DESIGN.md · 关键技术点 4.1 / 4.2 · 第 155–205 行"),

    ("04-文档-7-AGENTS-项目说明与运行.png", "AGENTS.md", 1, 38,
     "AGENTS.md · 项目说明与运行命令 · 第 1–38 行 / 共 190 行"),
    ("04-文档-8-AGENTS-目录约定与代码风格.png", "AGENTS.md", 39, 95,
     "AGENTS.md · 目录约定与代码风格 · 第 39–95 行"),
    ("04-文档-9-AGENTS-底线与测试要求.png", "AGENTS.md", 96, 145,
     "AGENTS.md · 绝对底线 / 性能 / 动效 / 测试要求 · 第 96–145 行"),
]


def find_browser():
    for p in CANDIDATES:
        if os.path.exists(p):
            return p
    raise SystemExit("找不到 Chrome / Edge")


def check_port_free(port):
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", port))
    except OSError:
        raise SystemExit(f"端口 {port} 被占用，请先关掉占用的程序")
    finally:
        s.close()


class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=90)
        self.i = 0

    def send(self, method, **params):
        self.i += 1
        self.ws.send(json.dumps({"id": self.i, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.i:
                if "error" in msg:
                    raise RuntimeError(f"{method} -> {msg['error']}")
                return msg.get("result", {})


def wait_devtools(port, timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2) as r:
                return json.load(r)
        except Exception:
            time.sleep(0.4)
    raise SystemExit("DevTools 端口没有起来")


def new_tab(port, url):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/json/new?{urllib.parse.quote(url, safe='')}",
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)


def close_tab(port, tab_id):
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json/close/{tab_id}", timeout=5).read()
    except Exception:
        pass


def build_html(body, badge):
    css = CSS.replace("__W__", str(WIDTH))
    return (
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        f"<style>{css}</style></head><body><div class=\"win\">"
        "<div class=\"bar\"><span class=\"dot r\"></span><span class=\"dot y\"></span>"
        "<span class=\"dot g\"></span><span class=\"tab\">预览 Markdown</span>"
        f"<span class=\"badge\">{badge}</span></div>"
        f"<div class=\"doc\">{body}</div></div></body></html>"
    )


def trim_bottom(path):
    """把底部与背景色相同的空白行裁掉。"""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    bg = im.getpixel((2, h - 4))
    last = 0
    px = im.load()
    step = 2
    for y in range(h - 1, -1, -step):
        row_diff = False
        for x in range(0, w, 37):
            if px[x, y] != bg:
                row_diff = True
                break
        if row_diff:
            last = y
            break
    if last and last < h - 12:
        im.crop((0, 0, w, min(h, last + 14))).save(path)
    return im.size


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    check_port_free(CDP_PORT)
    browser = find_browser()
    print(f"浏览器: {browser}")
    print(f"输出目录: {OUT}\n")

    proc = subprocess.Popen(
        [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            f"--remote-debugging-port={CDP_PORT}",
            f"--user-data-dir={PROFILE}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        wait_devtools(CDP_PORT)
        for name, src, start, end, badge in BANDS:
            src_path = os.path.join(ROOT, src)
            with open(src_path, "r", encoding="utf-8") as f:
                all_lines = f.read().splitlines()
            fragment = "\n".join(all_lines[start - 1:end])
            body = markdown.markdown(
                fragment,
                extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
            )
            html_path = os.path.join(TMP, name.replace(".png", ".html"))
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(build_html(body, badge))

            url = "file:///" + urllib.parse.quote(html_path.replace("\\", "/"), safe="/:")
            tab = new_tab(CDP_PORT, url)
            cdp = CDP(tab["webSocketDebuggerUrl"])
            cdp.send("Page.enable")
            time.sleep(0.6)
            cdp.send(
                "Emulation.setDeviceMetricsOverride",
                width=WIDTH,
                height=1000,
                deviceScaleFactor=DSF,
                mobile=False,
            )
            time.sleep(0.4)
            res = cdp.send(
                "Page.captureScreenshot",
                format="png",
                captureBeyondViewport=True,
                optimizeForSpeed=False,
            )
            out_path = os.path.join(OUT, name)
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(res["data"]))

            # 内容不足一屏时，截图底部会留一条 body 背景色的空白，按 .win 的实际高度裁掉
            m = cdp.send(
                "Runtime.evaluate",
                expression="document.querySelector('.win').getBoundingClientRect().height",
                returnByValue=True,
            )
            win_h = float(m["result"]["value"])
            cdp.ws.close()
            close_tab(CDP_PORT, tab["id"])

            im = Image.open(out_path)
            want = int(round(win_h * DSF))
            if 0 < want < im.size[1]:
                im.crop((0, 0, im.size[0], want)).save(out_path)
                im = Image.open(out_path)

            size = os.path.getsize(out_path)
            print(f"  {name}  {im.size[0]}x{im.size[1]}  {size:,} 字节")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        time.sleep(0.4)

    print(f"\n完成，共 {len(BANDS)} 张，已存到 {OUT}")


if __name__ == "__main__":
    sys.exit(main())