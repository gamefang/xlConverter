@echo off
pyinstaller -F xl2json.py
copy xl2json_conf.json .\dist\xl2json_conf.json
pause