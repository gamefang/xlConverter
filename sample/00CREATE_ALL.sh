#!/bin/bash
# 依賴: openpyxl
# Win: pip install openpyxl
# Ubuntu24+: sudo apt install python3-openpyxl && sudo apt-mark manual python3-openpyxl
#==============================================================
# 配置導表工具目錄
FOLDER_TOOL="/mnt/GAME/git/xl_converter"
#==============================================================

# 需保持設置ini始終與sh同級，位於實際項目文件夾內
CUR_DIR=$(dirname "$0")
FP_INI="$CUR_DIR/xl_converter.toml"

# 跳轉工具目錄
cd "$FOLDER_TOOL"
# 區分win與linux系統，使用不同Python命令
OS_NAME=$(uname)
if [[ "$OS_NAME" == *"MSYS"* || "$OS_NAME" == *"CYGWIN"* ]]; then
	py -u xl_converter/xl_converter.py --fp "$FP_INI"
else
	python -u xl_converter/xl_converter.py --fp "$FP_INI"
fi

echo "Press any key to exit..."
read -n 1
