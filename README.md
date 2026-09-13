# FloatNote

A lightweight sticky-notes widget for Windows 10/11 with native acrylic blur, global hotkeys, and system tray integration.

## Development

Install dependencies and run the app:

```powershell
pip install -r requirements.txt
python main.py
```

Notes are saved to `%USERPROFILE%\Documents\FloatNote\notes.txt`. Press **Ctrl+Shift+N** to toggle show/hide.

## Building the Installer

From the project root:

```powershell
pip install -r requirements.txt
pyinstaller build/floatnote.spec
```

Then compile the installer with [Inno Setup 6](https://jrsoftware.org/isinfo.php):

```powershell
iscc floatnote.iss
```

The setup executable is written to `dist\FloatNoteSetup.exe`. It installs FloatNote to `%LOCALAPPDATA%\FloatNote` and adds a Start Menu shortcut.

## SmartScreen Notice

The built `.exe` is not code-signed. On first run on any machine, Windows SmartScreen may show an **"unrecognized app"** warning. This is expected for unsigned software — click **More info**, then **Run anyway**. It is not a bug in FloatNote.
