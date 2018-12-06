@echo off
pyinstaller -F xlConverter.py
copy xlConverter.ini .\dist\xlConverter.ini
pause