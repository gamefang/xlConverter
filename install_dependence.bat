REM 最新版的xlrd不支持xlsx文件了，需要改为老版本
@echo off
pip uninstall xlrd
pip install xlrd==1.2.0
pause