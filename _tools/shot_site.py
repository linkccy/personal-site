"""给个人网站拍截图（证据留存用，不参与构建）。

做法：python http.server 起静态服务 -> Chrome 无头 + CDP ->
设置设备尺寸 -> 强制把入场动画置为终态 -> 截整页图。

用法：python _tools/shot_site.py
"""
import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

import websocket

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(ROOT, "dist")
OUT = os.path.join(os.path.dirname(ROOT), "第七天作业截图")
PORT = 5199
CDP_PORT = 9250
PROFILE = os.path.join(os.environ.get("TEMP", "."), "cdp_site_profile")

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

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


def free_ports(check_site_port=True):
    ports = (PORT, CDP_PORT) if check_site_port else (CDP_PORT,)
    for port in ports:
        s = socket.socket()
        try:
            s.bind(("127.0.0.1", port))
        except OSError:
            raise SystemExit(f"端口 {port} 被占用，请先关掉占用的程序")
        finally:
            s.close()


class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=60)
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
    url = f"http://127.0.0.1:{port}/json/version"
    end = time.time() + timeout
    while time.time() < end:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                return json.load(r)
        except Exception:
            time.sleep(0.4)
    raise SystemExit("DevTools 端口没有起来")


def new_tab(port, target_url):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/json/new?{urllib.parse.quote(target_url, safe='')}",
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)


def shot(cdp, out_path, width, height, full=True, scale=1.0, dsf=2):
    cdp.send(
        "Emulation.setDeviceMetricsOverride",
        width=width,
        height=height,
        deviceScaleFactor=dsf,
        mobile=width < 700,
    )
    time.sleep(0.7)
    cdp.send("Runtime.evaluate", expression=FORCE_FINAL)
    time.sleep(0.5)
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
    if not os.path.isdir(DIST):
        raise SystemExit("dist 不存在，先跑 npm run build")
    os.makedirs(OUT, exist_ok=True)
    # 有时静态服务由外部单独启动（比如在另一个终端里跑），
    # 这时设 SKIP_SERVER=1，脚本就只负责截图。
    skip_server = os.environ.get("SKIP_SERVER") == "1"
    free_ports(check_site_port=not skip_server)
    browser = find_browser()
    print("浏览器:", browser)

    server = None
    if skip_server:
        print("跳过启动静态服务（SKIP_SERVER=1），直接连 127.0.0.1:%d" % PORT)
    else:
        server = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(PORT), "--directory", DIST],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    chrome = None
    try:
        time.sleep(1.2)
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=5) as r:
            print("本地服务 HTTP", r.status)

        if os.path.isdir(PROFILE):
            shutil.rmtree(PROFILE, ignore_errors=True)

        chrome = subprocess.Popen(
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
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        wait_devtools(CDP_PORT)

        pages = json.load(
            urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/list", timeout=10)
        )
        page = next(p for p in pages if p["type"] == "page")
        cdp = CDP(page["webSocketDebuggerUrl"])
        cdp.send("Page.enable")
        cdp.send("Runtime.enable")
        cdp.send("Page.navigate", url=f"http://127.0.0.1:{PORT}/")
        time.sleep(3.0)

        title = cdp.send("Runtime.evaluate", expression="document.title", returnByValue=True)
        print("页面标题:", title["result"]["value"])

        jobs = [
            ("第七天-01-整页-桌面.png", 1440, 900, True, 1),
            ("第七天-02-首屏-桌面.png", 1440, 900, False, 1),
            ("第七天-03-整页-手机.png", 390, 844, True, 2),
            ("第七天-04-首屏-手机.png", 390, 844, False, 2),
            ("第七天-05-整页-平板.png", 834, 1112, True, 2),
        ]
        for name, w, h, full, dsf in jobs:
            path = os.path.join(OUT, name)
            size = shot(cdp, path, w, h, full=full, dsf=dsf)
            print(f"  {name}  {w}x{h}  {size / 1024:.0f} KB")

        # 顺便检查几个关键点
        checks = cdp.send(
            "Runtime.evaluate",
            returnByValue=True,
            expression="""
            JSON.stringify({
              scrollW: document.documentElement.scrollWidth,
              clientW: document.documentElement.clientWidth,
              sections: [...document.querySelectorAll('section[id]')].map(s => s.id),
              skillsFilled: [...document.querySelectorAll('.skill-fill')]
                  .every(e => parseFloat(e.style.width) > 0),
              canvas: !!document.querySelector('#starfield'),
              starPixels: (() => {
                const c = document.querySelector('#starfield');
                const ctx = c.getContext('2d');
                const d = ctx.getImageData(0, 0, Math.min(400, c.width), Math.min(400, c.height)).data;
                let n = 0;
                for (let i = 3; i < d.length; i += 4) if (d[i] > 10) n++;
                return n;
              })(),
            })
            """,
        )
        info = json.loads(checks["result"]["value"])
        print("自检:", json.dumps(info, ensure_ascii=False))
        if info["scrollW"] > info["clientW"]:
            print("  ⚠ 出现横向滚动！")
        if info["starPixels"] == 0:
            print("  ⚠ 星空没有绘制出像素！")

        # 博客展开 + 复制按钮
        cdp.send(
            "Runtime.evaluate",
            expression="document.querySelectorAll('.post-toggle')[0].click()",
        )
        time.sleep(0.6)
        cdp.send(
            "Runtime.evaluate",
            expression="document.getElementById('blog').scrollIntoView({behavior:'instant'})",
        )
        time.sleep(0.6)
        cdp.send("Emulation.setDeviceMetricsOverride", width=1440, height=1000, deviceScaleFactor=1, mobile=False)
        time.sleep(0.4)
        cdp.send("Runtime.evaluate", expression=FORCE_FINAL)
        time.sleep(0.4)
        res = cdp.send("Page.captureScreenshot", format="png", captureBeyondViewport=False)
        open(os.path.join(OUT, "第七天-06-博客展开.png"), "wb").write(
            base64.b64decode(res["data"])
        )
        print("  第七天-06-博客展开.png")

        # 联系方式区：确认邮箱渲染正确
        cdp.send(
            "Runtime.evaluate",
            expression="document.getElementById('contact').scrollIntoView({behavior:'instant'})",
        )
        time.sleep(0.6)
        cdp.send("Runtime.evaluate", expression=FORCE_FINAL)
        time.sleep(0.4)
        res = cdp.send("Page.captureScreenshot", format="png", captureBeyondViewport=False)
        open(os.path.join(OUT, "第七天-07-联系方式.png"), "wb").write(
            base64.b64decode(res["data"])
        )
        email = cdp.send(
            "Runtime.evaluate",
            returnByValue=True,
            expression="document.querySelector('.contact-value').textContent",
        )
        print("  第七天-07-联系方式.png   页面上显示的邮箱:", email["result"]["value"])
        cdp.ws.close()
    finally:
        if chrome:
            chrome.terminate()
        if server:
            server.terminate()
        shutil.rmtree(PROFILE, ignore_errors=True)
    print("输出目录:", OUT)


if __name__ == "__main__":
    import urllib.parse  # noqa: E402  (new_tab 里用到，放在这里避免污染顶部)

    main()