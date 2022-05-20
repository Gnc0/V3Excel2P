# V3Excel2P

Tools that transfer excel to P for Vicotira3 ; 维多利亚3的转表工具

## 说明

该工具可用来将excel的配置转为V3所需的配置文件，点击excel\Transfer.bat即可将excel转为txt

详细范本可见excel/【数值设定】生产方式.xlsx；具体表格规则也在里面

该工具基于python3.10、lua5.4、bat运行

## 使用环境

1、路径不能含有中文目录

2、使用python_tools3.10，不支持win7

## 工具添加说明

excel下的Transfer.bat自动调用Scripts的main.py

Transfer.bat会传根目录的路径传进去，你可以通过sys.argv[1]来获得它

有些人的环境可能不会传入路径的最后一个'\'，所以最好写判断来添加'\'

如果你有自己的工具，直接覆盖main.py即可；如果会写工具，那学个bat也是很轻松的

## python库的添加支持

目前下载的库包括numpy、pandas、oepnpyxl和xlrd

如果你需要额外扩展python的库，那么以下是numpy的扩展代码，建个bat文件把这些粘贴进去，把numpy改成你想要
的库的名字即可

但是要注意有些库的安装，如果先后顺序乱了，可能会出问题，导致该目录的python报废，所以最好复制一份做备份

    @echo off
    cd ../python_tools/toolVenv/Scripts
    pip.exe install numpy -t ../Lib/site-packages
    pause
