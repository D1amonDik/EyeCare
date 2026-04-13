# Build Instructions for EyeCare

## Creating Windows Executable

### Method 1: PyInstaller (Recommended)

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
```bash
pyinstaller --name="EyeCare" --onefile --windowed --icon=icon.ico main.py
```

3. The executable will be in `dist/EyeCare.exe`

### Method 2: PyInstaller with all dependencies

```bash
pyinstaller --name="EyeCare" ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --add-data "localization.py;." ^
    --hidden-import=pystray ^
    --hidden-import=PIL ^
    --hidden-import=pynput ^
    --hidden-import=screeninfo ^
    --hidden-import=psutil ^
    main.py
```

### Method 3: Auto-py-to-exe (GUI Tool)

1. Install auto-py-to-exe:
```bash
pip install auto-py-to-exe
```

2. Run the GUI:
```bash
auto-py-to-exe
```

3. Configure:
   - Script Location: `main.py`
   - Onefile: One File
   - Console Window: Window Based (hide the console)
   - Icon: Select `icon.ico` if available
   - Additional Files: Add `localization.py`

4. Click "Convert .py to .exe"

## Testing the Executable

1. Copy `EyeCare.exe` to a clean folder
2. Run it - it should create `config.json` and `stats.json` automatically
3. Test all features:
   - Settings window opens on first run
   - Language switching works
   - Break window appears
   - Tray icon works
   - Statistics are saved

## Creating a Release

1. Build the executable
2. Create a ZIP file with:
   - EyeCare.exe
   - README.md
   - LICENSE (if you have one)

3. Upload to GitHub Releases

## Troubleshooting

### "Module not found" errors
- Add missing modules with `--hidden-import=module_name`

### Large file size
- Use `--exclude-module` to remove unused modules
- Example: `--exclude-module matplotlib --exclude-module numpy`

### Icon not showing
- Make sure `icon.ico` exists in the project folder
- Use absolute path: `--icon=C:\path\to\icon.ico`

### App crashes on startup
- Test with `--console` first to see error messages
- Check if all dependencies are included
