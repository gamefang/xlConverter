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
