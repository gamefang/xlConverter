#!/bin/bash
# 依賴: openpyxl
# Win: pip install openpyxl
# Ubuntu24+: sudo apt install python3-openpyxl && sudo apt-mark manual python3-openpyxl
#==============================================================
# 配置導表工具的項目路徑（絕對路徑或相對於此文件路徑）
FOLDER_TOOL="/mnt/GAME/git/xl_converter"
# .gitattributes文件路徑（絕對路徑或相對於此文件路徑）
GITATTRIBUTES_FILE="../.gitattributes"
# 是否自動創建.gitattributes(優化換行符處理)
AUTOGEN_GITATTRIBUTES_FILE=true
#==============================================================

# 需保持設置ini始終與sh同級，位於實際項目文件夾內
CUR_DIR=$(dirname "$0")
FP_INI="$CUR_DIR/xl_converter.toml"
FP_ATTR="$CUR_DIR/$GITATTRIBUTES_FILE"

# 跳轉工具目錄
cd "$FOLDER_TOOL"
# 區分win與linux系統，使用不同Python命令
OS_NAME=$(uname)
if [[ "$OS_NAME" == *"MSYS"* || "$OS_NAME" == *"CYGWIN"* ]]; then
	py -u xl_converter/xl_converter.py --fp "$FP_INI"
else
	python -u xl_converter/xl_converter.py --fp "$FP_INI"
fi

# 優化換行符處理
if [ ! -f "$FP_ATTR" ]; then
	if [ "$AUTOGEN_GITATTRIBUTES_FILE" == "true" ]; then
    		cat > "$FP_ATTR" << EOF
# Normalize EOL for all files that Git considers text files.
* text=auto eol=lf
EOF
	    echo ".gitattributes generated: <$FP_ATTR>"
	fi
fi
git add --renormalize .

echo "Press any key to exit..."
read -n 1
