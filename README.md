# 🛸 Advanced Remote Administration Tool (RAT)

[![Discord](https://img.shields.io/badge/Discord-Join%20Our%20Server-7289da?style=for-the-badge&logo=discord)](https://discord.gg/AghBF8aFeX)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge&logo=opensourceinitiative)](https://opensource.org/licenses/MIT)

A sophisticated, single-file administration utility designed for remote Windows management via Discord. Built with stealth, persistence, and reliability in mind.

---

## 📢 Join the Community
Have questions? Need help? Join our Discord server for updates and support:  
👉 **[Join our Discord Server](https://discord.gg/AghBF8aFeX)**

---

## 🚀 Quick Start

1. **Install Dependencies**:
   Ensure you have Python 3.8+ installed, then run the following command to install all necessary modules:
   ```bash
   pip install discord.py python-dotenv opencv-python pywin32 requests psutil pillow sounddevice scipy pyttsx3 wmi
   ```

2. **Configure Credentials**:
   Create a `.env` file in the same directory as `main.py` and add your bot credentials:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   GUILD_ID=your_server_id_here
   ```

3. **Run the Bot**:
   ```bash
   python main.py
   ```
   On the first run, the bot will automatically create a unique channel in your Discord server named after the PC's hostname.

---

## 🛠️ Command Categories

### 🌐 Reconnaissance & System Info
- `!sysinfo` - Captures Public IP, Local IP, MAC, HWID, CPU/GPU specs, and RAM.
- `!wifi` - Recovers all saved WiFi profiles and their clear-text passwords.

### 📸 Media Capture
- `!webcam` - Takes a silent photo from the default webcam.
- `!ss` - Captures a screenshot of all connected monitors.
- `!audio [seconds]` - Records high-fidelity audio from the microphone (default 5s).

### 📁 File & Shell Management
- `!shell <command>` - Executes any PowerShell command.
  - *Smart Persistence*: Intercepts `cd` commands to update the bot's working directory across restarts.
  - *Auto-upload*: If output > 2000 chars or it's a directory listing (`ls`, `dir`), it uploads a `.txt` file instead.
- `!search <dir> <filename>` - Recursively searches for a file starting from the specified directory.
- `!upload` - Save any file attached to the Discord message to the current directory on the PC.
- `!download <path>` - Sends a file from the host PC to the Discord channel.

### 🔋 Power & UI Control
- `!power <action>` - Execute system power commands.
  - Actions: `shutdown`, `restart`, `logout`, `lock`.
- `!taskbar <hide/show>` - Toggles the visibility of the Windows taskbar.
- `!msg <text>` - Pops up a native Windows message box with the specified text.
- `!tts <text>` - Uses the system's text-to-speech to read a message aloud.

### 🧹 Maintenance & Integration
- `!clear [amount]` - Purges message history in the Discord channel.
- `!help` - Displays a paginated menu of all available commands.
- **Auto-Heartbeat**: The bot sends a status update every 10 minutes to confirm it is still online.

---

## 🔒 Security & Stealth Features

- **Registry Persistence**: Automatically adds itself to `HKCU\Run` so it starts with Windows.
- **Hidden Execution**: All system commands are run with `CREATE_NO_WINDOW` to prevent flickering consoles.
- **Single Instance Check**: Uses advanced logic to ensure only one bot instance is active, preventing duplicate responses.
- **Robust Error Handling**: Every command is wrapped in try-except blocks to prevent crashes.

---

## ⚠️ Ethical Disclaimer
This tool is for **educational** and **authorized system administration** purposes only. Unauthorized access to computer systems is strictly prohibited and illegal. The author is not responsible for any misuse of this software.

---

### 💬 Get in Touch
[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/AghBF8aFeX)

**Made with ❤️ for the Community**
