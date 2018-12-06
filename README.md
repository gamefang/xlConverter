# xlConverter

- convert xls/xlsx to other data.
- custom any of file,sheet,area,row,column... , to be converted or not.
- various data types, include json and md etc.

------------

## Convertion Samples

### Default 2-Dimensional Data

- from excel

|sKey|iParam1|iParam2|
|:--|:--|:--|
|1|10|20|
|2|15|25|
|3|25|35|

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

# xlConverter汉语版说明

- 可将Excel文档转化为其它数据文件。
- 自由控制任意文件、工作表、区域、行、列的转化与否。
- 支持多种文件格式，包括json、md等。
- 相关链接：
	[项目地址](https://github.com/gamefang/xlConverter "项目地址")
	
------------

## 用法

- 调整xlConverter.ini中相关配置。
- 按格式调整Excel文件。
- 运行python源码或exe输出。

------------

## 转化示例

### 默认二维表

- Excel表格

|sKey|iParam1|iParam2|
|:--|:--|:--|
|1|10|20|
|2|15|25|
|3|25|35|

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

- json数据

```
[
    3,
    6,
    9
]
```

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
- version1.3.5
	2018/11/29 添加横向键值对的导出方式。
- version1.4.0
	2018/11/29-12/5 重构xlConverter。