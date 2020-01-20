@echo off
pyinstaller -F -i icon.ico xlConverter.py
copy xlConverter.ini .\dist\xlConverter.ini
pause