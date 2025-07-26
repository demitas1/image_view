# Image view

## Install

```
pip install -r requrements.txt
```

## Usage

- image view

```
python image_view.py <directory>
```

  - LMB / Right:  Next image
  - RMB / Left:   Previous image
  - MMB / Space:   Context Menu
  - R:  Toggle random order
  - H:  Toggle H-flip
  - Ctrl + C: Copy image
  - Q:  Quit

## Build

```
# in venv
pip install pyinstaller

# build
pyinstaller --onefile --windowed image-viewer

# executable
ls dist/image-viewer
```

# License

- GPL v3

- Icon files are licensed under MIT by https://feathericons.com/
