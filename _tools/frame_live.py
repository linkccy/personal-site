"""把线上站点的截图套进「浏览器窗口」外框里，让地址栏一起入镜。

交作业用：只截网页内容看不出「这是公网地址」，把地址栏带上就是直接证据。

用法：python _tools/frame_live.py
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

import websocket
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(os.path.dirname(ROOT), "第七天作业截图")
OUT = os.path.join(os.path.dirname(ROOT), "第七天提交截图")
TMP = os.path.join(os.environ.get("TEMP", "."), "framelive")
CDP_PORT = 9256
PROFILE = os.path.join(os.environ.get("TEMP", "."), "cdp_frame_profile")

URL = "https://linkccy.github.io/personal-site/"
TITLE = "chaoyi · 个人主页"

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

CSS = """
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #101014; }
body { font-family: "Microsoft YaHei", "Segoe UI", system-ui, sans-serif; padding: 22px; }
.win { border-radius: 12px; overflow: hidden; border: 1px solid #3a3a3f;
       background: #202024; box-shadow: 0 18px 50px rgba(0,0,0,.55); }
.bar { height: 46px; background: #2b2b30; display: flex; align-items: center;
       gap: 9px; padding: 0 14px; border-bottom: 1px solid #3a3a3f; }
.dot { width: 13px; height: 13px; border-radius: 50%; flex: 0 0 auto; }
.r { background: #ff5f57; } .y { background: #febc2e; } .g { background: #28c840; }
.tab { margin-left: 16px; background: #202024; color: #d8d8d8; font-size: 13px;
       padding: 6px 16px; border-radius: 7px 7px 0 0; display: flex; align-items: center;
       gap: 8px; }
.tab .fav { width: 14px; height: 14px; border-radius: 3px;
            background: linear-gradient(135deg, #22d3ee, #818cf8, #c084fc); }
.urlbar { height: 42px; background: #232327; display: flex; align-items: center;
          padding: 0 16px; gap: 10px; border-bottom: 1px solid #3a3a3f; }
.pill { flex: 1; height: 28px; background: #17171a; border: 1px solid #3a3a3f;
        border-radius: 14px; display: flex; align-items: center; padding: 0 14px;
        gap: 9px; }
.lock { font-size: 12px; color: #28c840; }
.url { font-family: Consolas, "Cascadia Mono", monospace; font-size: 13.5px;
       color: #cfd3dc; }
.shot { display: block; width: 100%; }
"""


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


def build_html(png_path, width, extra_style=""):
    with open(png_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return (
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        f"<style>{CSS}{extra_style}</style></head><body>"
        f"<div class=\"win\" style=\"width:{width}px\">"
        "<div class=\"bar\"><span class=\"dot r\"></span><span class=\"dot y\"></span>"
        "<span class=\"dot g\"></span>"
        f"<span class=\"tab\"><span class=\"fav\"></span>{TITLE}</span></div>"
        "<div class=\"urlbar\"><div class=\"pill\">"
        f"<span class=\"lock\">&#128274;</span><span class=\"url\">{URL}</span>"
        "</div></div>"
        f"<img class=\"shot\" src=\"data:image/png;base64,{b64}\">"
        "</div></body></html>"
    )


def capture(cdp, width, full=True, dsf=2):
    cdp.send(
        "Emulation.setDeviceMetricsOverride",
        width=width,
        height=900,
        deviceScaleFactor=dsf,
        # 注意：不要开 mobile=True —— 没有 viewport meta 的页面会被当成 980px 宽的
        # 移动视口，浏览器自作主张把布局宽度改成 980，截出来就对不上了。
        mobile=False,
    )
    time.sleep(0.7)
    res = cdp.send(
        "Page.captureScreenshot",
        format="png",
        captureBeyondViewport=full,
        optimizeForSpeed=False,
    )
    return base64.b64decode(res["data"])


def make_crop(src, dst, box):
    im = Image.open(src)
    im.crop(box).save(dst)
    return Image.open(dst).size


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    check_port_free(CDP_PORT)

    # --- 准备输入：手机首屏从手机整页图顶部裁出来 ---
    mobile_full = os.path.join(ASSETS, "第七天-10-线上-整页-手机.png")
    mobile_top = os.path.join(TMP, "_mobile_top.png")
    size = make_crop(mobile_full, mobile_top, (0, 0, 390 * 2, 844 * 2))
    print(f"手机首屏裁切: {size[0]}x{size[1]}")

    jobs = [
        # (输出名, 源图, 浏览器窗口宽度(CSS px), 页面总宽)
        ("05-网页-1-线上首屏（带地址栏）.png",
         os.path.join(ASSETS, "第七天-08-线上-首屏-桌面.png"), 1440, 1440 + 44),
        ("05-网页-3-线上手机端（带地址栏）.png", mobile_top, 390, 390 + 44),
    ]

    browser = find_browser()
    print(f"浏览器: {browser}\n")
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
        for name, src, win_w, page_w in jobs:
            if not os.path.exists(src):
                print(f"  跳过 {name}：找不到 {src}")
                continue
            html_path = os.path.join(TMP, name.replace(".png", ".html"))
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(build_html(src, win_w))
            url = "file:///" + urllib.parse.quote(html_path.replace("\\", "/"), safe="/:")
            tab = new_tab(CDP_PORT, url)
            cdp = CDP(tab["webSocketDebuggerUrl"])
            cdp.send("Page.enable")
            time.sleep(0.8)
            data = capture(cdp, page_w)
            out_path = os.path.join(OUT, name)
            with open(out_path, "wb") as f:
                f.write(data)
            cdp.ws.close()
            close_tab(CDP_PORT, tab["id"])
            im = Image.open(out_path)
            print(f"  {name}  {im.size[0]}x{im.size[1]}  {os.path.getsize(out_path):,} 字节")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        time.sleep(0.4)

    # --- 整页长图直接复制过去（不套外框，保留全部分辨率） ---
    src_full = os.path.join(ASSETS, "第七天-09-线上-整页-桌面.png")
    dst_full = os.path.join(OUT, "05-网页-2-线上整页.png")
    if os.path.exists(src_full):
        with open(src_full, "rb") as fi, open(dst_full, "wb") as fo:
            fo.write(fi.read())
        im = Image.open(dst_full)
        print(f"  05-网页-2-线上整页.png  {im.size[0]}x{im.size[1]}  {os.path.getsize(dst_full):,} 字节")

    print(f"\n完成，已存到 {OUT}")


if __name__ == "__main__":
    sys.exit(main())