#!/bin/bash

# 保持設置ini始終與sh同級，位於實際項目文件夾內
cur_dir=$(dirname "$0")
fp="$cur_dir/xl_converter.ini"

# 指定xlConvert的本地位置，與項目無關
cd D:/Projects/xlConverter
export PYTHONPATH="$PWD"
python -u xl_converter/xl_converter.py --fp "$fp"

echo "Press any key to exit..."
read -n 1