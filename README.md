# xl2json

- convert xls/xlsx to json data.
- custom any of file,sheet,area,row,column... , to be converted or not.
- various styles of json data.

------------

## Convertion Samples

### Default 2-Dimensional Data

- from excel

|sKey|iParam1|iParam2|
|:--|:--|:--|
|1|10|20|
|2|15|25|
|3|25|35|

- over python

```
[
	['sKey','iParam1','iParam2'],
	['1',10,20],
	['2',15,25],
	['3',25,35]
]
```

- to json: default style: keys and k-v objects in a big object

```
{
    "1": {
      "Param1": 10,
      "Param2": 20
    },
    "2": {
      "Param1": 15,
      "Param2": 25
    },
    "3": {
      "Param1": 25,
      "Param2": 35
    }
}
```

- to json: style 1: k-v objects in array

```
[
    {
	  "Key":"1",
      "Param1": 10,
      "Param2": 20
    },
    {
	  "Key":"2", 
      "Param1": 15,
      "Param2": 25
    },
    {
	  "Key":"3",
      "Param1": 25,
      "Param2": 35
    }
]
```

------------

### 1-Dimensional Data

- from excel

|iNum|
|:--|
|3|
|6|
|9|

- over python

```
[
	['iNum'],
	[3],
	[6],
	[9]
]
```

- to json

```
[
    3,
    6,
    9
]
```

------------

## Usage and Configs

------------

# xl2json汉语版说明

- 可将Excel文档转化为json文件。
- 自由控制任意文件、工作表、区域、行、列的转化与否。
- 支持多种结构的json文件。
- 相关链接：
	[下载源代码](https://github.com/gamefang/xl2json "下载源代码")
	[最新Exe版本](https://github.com/gamefang/xl2json/releases/download/xl2json1.2/xl2json1.2.rar "最新Exe版本")
------------

## 用法

- 下载源代码，安装Python3.6及以上版本，正确配置后直接命令行使用：
```
xl2json.py --style 0
```
- Windows系统使用release版本，但仍需要正确的配置与格式。在cmd中输入：
```
xl2json --style 0
```

------------

## 转化示例

### 默认二维表

- Excel表格

|sKey|iParam1|iParam2|
|:--|:--|:--|
|1|10|20|
|2|15|25|
|3|25|35|

- Python运行过程

```
[
	['sKey','iParam1','iParam2'],
	['1',10,20],
	['2',15,25],
	['3',25,35]
]
```

- json数据
	默认结构：大对象内的 主键 - 键值对

```
{
    "1": {
      "Param1": 10,
      "Param2": 20
    },
    "2": {
      "Param1": 15,
      "Param2": 25
    },
    "3": {
      "Param1": 25,
      "Param2": 35
    }
}
```

- json数据
	风格1：数组内的键值对对象

```
[
    {
	  "Key":"1",
      "Param1": 10,
      "Param2": 20
    },
    {
	  "Key":"2", 
      "Param1": 15,
      "Param2": 25
    },
    {
	  "Key":"3",
      "Param1": 25,
      "Param2": 35
    }
]
```

------------

### 一维数据

- Excel表格

|iNum|
|:--|
|3|
|6|
|9|

- Python运行过程

```
[
	['iNum'],
	[3],
	[6],
	[9]
]
```

- json数据

```
[
    3,
    6,
    9
]
```

------------

## 配置与格式

### 配置文件说明

```
    配置文件可调整部分功能，需要严格遵循json格式。
    @xl_dir: Excel文件的存放目录，会自动搜寻目录下所有Excel文件。路径分隔符必须用“/”！
    @json_dir: 输出json文件的目录。路径分隔符必须用“/”！
    @recursive_xl_files: 是否采用递归形式搜索Excel文件目录。
    @output_in_one: 如果为false或0，则分别输出json文件，文件名为Excel对应sheet名；
                    如果为字符串，则输出至一个文件，例如填写config.json，则将所有Excel文件内容输出至该文件中。
    @file_exts: 搜寻的Excel文件後缀。另外默认以'~$','__'开头的excel文件不会被搜寻。
    @sheet_name_prefix: Excel文件中，加此前缀的sheet会被导出，可支持多个。前缀只允许一个字符。
    @bound_tag: Excel一个sheet中配置的边界符号，只有边界内的配置内容才会被导出。
    @note_signs: Excel配置中单行、单列注释的前缀，被注释则不会被导出。
    @allow_inner_note: 是否允许Excel配置中使用内容注释（可能导致字段不统一）。 	
    @var_type_pre: Excel配置中字段名前缀字符串，用以区分数据类型，需严格按照以下顺序：
        0-python的int，对应json中的数字num；
        1-python的float，对应json中的数字num；
        2-python的string，对应json中的字符串string；
        3-借用python的tuple，对应json中的全字符串数组（自动补全双引号）;
        4-python的list，对应json中的普通数组array（全数字或数串混合自补双引号）；
        5-python的dict，对应json中的对象object（自补双引号）；
        6-python的boolean，对应json中的布尔值bool；
        暂不包括json中的null类型。
    @keep_var_type: 是否在json的key中保留字段名前缀。
    @read_me_mode: 是否查看说明。
```

### Excel文件格式说明

- [工作簿]需要导出的所有Excel文件必须放在配置文件夹中。
- [工作表]需要导出的sheet页前需加前缀，如分开导出则json文件名为前缀後的sheet名。
- [导出区域]需要导出的区域要用边界符号框住，位置为右上和左下。
- [字段名称]右上边界符号所在行必须为表头，第一个字符表示字段的数据类型，详见配置文件说明的var_type_pre字段说明。
- [数据规范]同列Excel数据需要遵循字段的数据类型，否则会产生错误。
		数字：Excel所见即所得；
        字符串：无需添加两侧""；
        数组：无需添加两侧[]，但其中嵌套内容需严格遵循json模式，暂不支持浮点型数据；
        对象：无需添加两侧{}，但其中嵌套内容需严格遵循json模式，暂不支持浮点型数据；
        布尔值：Excel所见即所得。
		不导出数据：由note_signs开头的数据不被导出，需要打开allow_inner_note开关。
		
------------

## 版本记录

- version1.3
	2018/11/6 添加内容注释功能，可选择性屏蔽部分key的部分字段
- version1.3.1
	2018/11/7 添加是否递归搜索Excel文件夹的选项
- version1.3.2
	2018/11/9 优化JSON配置文件加载错误处理
- version1.3.3
	2018/11/15 添加对日期格式输出的支持。只输出为字符串。
- version1.3.4
	2018/11/20 优化浮点数导出，最多保留8位小数，避免excel累加出现的微小浮点数。