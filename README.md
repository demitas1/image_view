# Image view

## Install

### Linux/macOS

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
```

### Windows

```cmd
# 1. Install Python 3.8+ from python.org or Microsoft Store
# Make sure to check "Add Python to PATH" during installation

# 2. Verify installation
python --version
pip --version

# 3. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

## Usage

- Open files or diretory

**Linux/macOS:**

```bash
python src/image_viewer.py <directory>
python src/image_viewer.py -r <directory>  # recursive search
```

**Windows:**

```cmd
python src\image_viewer.py <directory>
python src\image_viewer.py -r <directory>  # recursive search
```

- Key assign

  - LMB / Right:  Next image
  - RMB / Left:   Previous image
  - MMB / Space:   Context Menu
  - R:  Toggle random order
  - H:  Toggle H-flip
  - Ctrl + C: Copy image
  - Q:  Quit

## Build

### Linux/macOS
```bash
# in venv
pip install pyinstaller

# build
pyinstaller image-viewer.spec

# executable
dist/image-viewer
```

### Windows
```cmd
# in activated venv
pip install pyinstaller

# build
pyinstaller image-viewer.spec

# executable
dist\image-viewer.exe
```

**Note:** Each platform requires building on that specific platform. Cross-compilation is not supported by PyInstaller.

# License

- GPL v3

- Icon files are licensed under MIT by https://feathericons.com/

# 🙏 Support Development

This project is developed in my free time. If you find it useful:

☕ [Buy me a coffee](https://www.buymeacoffee.com/demitas) - Helps keep me caffeinated for coding sessions!

⭐ Star this repo - It means a lot!
