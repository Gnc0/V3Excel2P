@echo off
chcp 65001
title transfer

set sourcePath=%~dp0
set rootPath=%sourcePath:~0,-6%

echo 当前root目录：%rootPath%
cd %rootPath%

del python_tools\toolVenv\pyvenv.cfg

call lua_tools\lua54.exe python_tools\toolVenv\setAddress.lua

call python_tools\toolVenv\Scripts\activate.bat %rootPath%python_tools\toolVenv
echo 激活虚拟环境成功！
python_tools\toolVenv\Scripts\python.exe scripts\main.py %rootPath%
call python_tools\toolVenv\Scripts\deactivate.bat
echo 关闭虚拟环境成功！

pause
