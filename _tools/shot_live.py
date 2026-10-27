"""给已经部署到 GitHub Pages 的线上站点拍截图（证据留存用，不参与构建）。

和 shot_site.py 的区别：那个拍本地 dist，这个直接拍公网地址，
用来证明「站点确实发布在公网、任何人打开都是这个样子」。

用法：python _tools/shot_live.py
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

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(os.path.dirname(ROOT), "第七天作业截图")
LIVE = "https://linkccy.github.io/personal-site/"
CDP_PORT = 9252
PROFILE = os.path.join(os.environ.get("TEMP", "."), "cdp_live_profile")

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

# 线上页面有 IntersectionObserver 淡入动画，截图前先把它推到终态，
# 否则会截到半透明的中间帧。
FORCE_FINAL = """
document.querySelectorAll('.reveal').forEach(function (e) {
  e.style.transition = 'none';
  e.classList.add('in');
});
document.querySelectorAll('.skill-fill').forEach(function (e) {
  var n = e.parentElement.getAttribute('aria-valuenow');
  e.style.transition = 'none';
  e.style.width = (n || 0) + '%';
});
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


def wait_ready(cdp, timeout=45):
    """等页面的 JS 把内容渲染出来（#root 里有子节点）。"""
    end = time.time() + timeout
    while time.time() < end:
        res = cdp.send(
            "Runtime.evaluate",
            expression="document.querySelector('#root') && document.querySelector('#root').children.length",
            returnByValue=True,
        )
        if res.get("result", {}).get("value"):
            return True
        time.sleep(0.5)
    return False


def shot(cdp, out_path, width, height, full=True, dsf=2):
    cdp.send(
        "Emulation.setDeviceMetricsOverride",
        width=width,
        height=height,
        deviceScaleFactor=dsf,
        mobile=width < 700,
    )
    time.sleep(0.9)
    cdp.send("Runtime.evaluate", expression=FORCE_FINAL)
    time.sleep(0.6)
    res = cdp.send(
        "Page.captureScreenshot",
        format="png",
        captureBeyondViewport=full,
        optimizeForSpeed=False,
    )
    data = base64.b64decode(res["data"])
    with open(out_path, "wb") as f:
        f.write(data)
    return len(data)


def main():
    os.makedirs(OUT, exist_ok=True)
    check_port_free(CDP_PORT)
    browser = find_browser()
    print(f"浏览器: {browser}")
    print(f"目标网址: {LIVE}")

    proc = subprocess.Popen(
        [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
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
        tab = new_tab(CDP_PORT, LIVE)
        cdp = CDP(tab["webSocketDebuggerUrl"])
        cdp.send("Page.enable")
        cdp.send("Runtime.enable")
        if not wait_ready(cdp):
            raise SystemExit("页面内容没渲染出来（#root 一直是空的）")

        # 顺手把线上页面读回来的关键信息打出来，作为「确实打开了真站点」的证据
        info = cdp.send(
            "Runtime.evaluate",
            expression=(
                "JSON.stringify({"
                "title: document.title,"
                "sections: Array.from(document.querySelectorAll('section[id]')).map(function(s){return s.id;}),"
                "canvas: !!document.querySelector('canvas'),"
                "email: (document.querySelector('.contact-value') || {}).textContent || '',"
                "scrollW: document.documentElement.scrollWidth,"
                "clientW: document.documentElement.clientWidth"
                "})"
            ),
            returnByValue=True,
        )
        print("线上自检:", info["result"]["value"])

        targets = [
            ("第七天-08-线上-首屏-桌面.png", 1440, 900, False),
            ("第七天-09-线上-整页-桌面.png", 1440, 900, True),
            ("第七天-10-线上-整页-手机.png", 390, 844, True),
        ]
        for name, w, h, full in targets:
            path = os.path.join(OUT, name)
            size = shot(cdp, path, w, h, full=full)
            print(f"已保存: {name}  ({size:,} 字节)")

        print("线上截图完成")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        time.sleep(0.5)


if __name__ == "__main__":
    sys.exit(main())