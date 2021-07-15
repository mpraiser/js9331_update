chcp 65001
pyinstaller -F update.py
cp -r firmware dist
cp properties.json dist