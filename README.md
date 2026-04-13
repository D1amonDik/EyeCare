# EyeCare

EyeCare is a minimalist eye-care reminder app designed to reduce eye strain during extended screen usage. It can also be used as a break time reminder app.

It provides customizable timers, full-screen break windows, 8 eye exercises, multi-language support, and a suite of additional features for a seamless user experience.

## ✨ Features

- ⏱️ **Customizable reminder timers** - set work and rest intervals
- 🌍 **Multi-language support** - English, Russian (Русский), Ukrainian (Українська)
- 🎨 **4 color themes** + custom theme with color picker
- 👁️ **8 eye exercises** - random exercise on each break to keep your eyes healthy
- 🔔 **Smart pause** - automatic pause when user is idle
- 🖥️ **Multi-monitor support** - choose which monitor to display break window on
- 📊 **Break statistics** - track daily and weekly breaks with visual progress
- 🎯 **Strict Mode** - mandatory breaks without skip option for disciplined rest
- 🔍 **Fullscreen app detection** - doesn't interrupt games and videos
- 🚀 **Windows autostart** - launch automatically on system startup
- 🎛️ **Customizable opacity** with live preview
- 🔊 **Custom sounds** - choose built-in sounds or load your own (MP3, WAV, OGG)
- 📍 **Window position saving** - configure break window size and position
- 🔄 **Settings reset** - quick return to default values

## 📖 The 20-20-20 Rule

The 20-20-20 rule is a guideline to reduce eye strain caused by staring at screens for extended periods. It suggests that for every 20 minutes spent looking at a screen, you should take a 20-second break and focus your eyes on something at least 20 feet (6 meters) away.

### Benefits:
- **Reduces Eye Strain**: Regular breaks help prevent eye fatigue and strain caused by prolonged screen time
- **Improves Focus**: Taking short breaks can help maintain focus and productivity throughout the day
- **Prevents Dry Eyes**: Looking away from the screen allows your eyes to blink more frequently, reducing the risk of dry eyes
- **Promotes Eye Health**: Focusing on distant objects helps relax eye muscles and reduce the risk of developing vision-related issues
- **Boosts Productivity**: By reminding users to take breaks, EyeCare helps maintain high levels of focus and motivation
- **Increases Workflow Efficiency**: Ensures you're working in manageable intervals, reducing burnout and fatigue
- **Encourages Healthy Habits**: Establishing a routine of regular breaks fosters a healthier work-life balance

## 🚀 Quick Start

### Download

**Option 1: Build from source** (Recommended)
```bash
git clone https://github.com/yourusername/eyecare.git
cd eyecare
pip install -r requirements.txt
python main.py
```

**Option 2: Build executable**
```bash
pip install pyinstaller
pyinstaller --clean --onefile --windowed --name="EyeCare" --add-data "localization.py;." main.py
# EXE will be in dist/EyeCare.exe
```

### Installation

- Python 3.12+
- Windows (primary platform)

### Installation from Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/eyecare.git
cd eyecare
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## 📦 Dependencies

### Required:
- `pystray` - system tray integration
- `Pillow` - image processing for tray icon
- `pynput` - mouse/keyboard activity detection
- `screeninfo` - multi-monitor support
- `psutil` - process management

### Optional:
- `pygame` - for custom sound playback (MP3, OGG)

## 🎮 Usage

After launch, the application minimizes to system tray. Right-click the tray icon to open menu:

- **Settings** - open settings window
- **Break Now** - start break immediately
- **Reset Timer** - reset current work timer
- **Exit** - close application

### Settings Tabs

#### ⏱ Timer
- Work time (1-60 minutes)
- Rest time (10-300 seconds)
- Smart pause with configurable idle threshold

#### 🎨 Appearance
- 4 built-in themes: Neon, Dark, Light, Ocean
- Custom theme with color picker
- Overlay opacity adjustment (0.1-1.0)
- Preview with resizable and movable window
- 4 sound options: Alert, Beep, Custom File, No Sound

#### ⚙ Behavior
- Fullscreen overlay mode
- Strict Mode (no skip button)
- Windows autostart
- Fullscreen app detection
- Monitor selection
- **Language selection** (English, Русский, Українська)

#### 📊 Statistics
- Today's progress with visual indicator
- Last 7 days history
- Total breaks all time
- Statistics reset

## 🌍 Supported Languages

- **English** (default)
- **Русский** (Russian)
- **Українська** (Ukrainian)

Language can be changed in Settings → Behavior → Language. Application restart required after language change.

## 🔨 Building Executable

To create a standalone `.exe` file:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
```bash
pyinstaller --name="EyeCare" --onefile --windowed --icon=icon.ico --add-data "localization.py;." main.py
```

3. The executable will be in the `dist/` folder

## 📁 Project Structure

```
eyecare/
├── main.py              # Entry point, tray, timer
├── settings_gui.py      # Settings window with 4 tabs
├── overlay.py           # Break window with exercises
├── config_manager.py    # Configuration management
├── stats_manager.py     # Break statistics
├── idle_detector.py     # Idle detection
├── localization.py      # Multi-language support
├── requirements.txt     # Python dependencies
├── .gitignore          # Ignored files
├── config.json         # Configuration (auto-created)
└── stats.json          # Statistics (auto-created)
```

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

Contributions for improving the UI, enhancing customizability, and adding new languages for multilingual support are particularly appreciated.

### How to Contribute:

1. Fork the repository to your GitHub account
2. Clone the repository to your local machine:
```bash
git clone https://github.com/your-username/eyecare.git
```
3. Create a new branch for your changes:
```bash
git checkout -b my-feature
```
4. Make changes to the code
5. Commit your changes:
```bash
git commit -m "Add new feature"
```
6. Push your changes to the remote repository:
```bash
git push origin my-feature
```
7. Create a pull request on GitHub

## 🐛 Known Limitations

- Primary support for Windows only
- Custom sounds (MP3/OGG) require pygame
- Fullscreen app detection works only on Windows

## 📝 License

MIT License

## 👤 Author

Created with ❤️ for your eye health

---

## Русская версия

EyeCare - минималистичное приложение для напоминаний об отдыхе для глаз. Поддержка 3 языков, 8 упражнений для глаз, настраиваемые интервалы, статистика перерывов и многое другое.

## Українська версія

EyeCare - мінімалістичний застосунок для нагадувань про відпочинок для очей. Підтримка 3 мов, 8 вправ для очей, налаштовувані інтервали, статистика перерв та багато іншого.
