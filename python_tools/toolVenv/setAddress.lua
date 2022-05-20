local obj=io.popen("cd")
local venv_path=obj:read("*all"):sub(1,-2)..'\\python_tools'
obj:close()

local cfgContent = 'home = '..venv_path..'\ninclude-system-site-packages = false\nversion = 3.10.4'

if testMode then print(cfgContent) end

local cfgFile_Write = io.open(venv_path..'\\toolVenv\\pyvenv.cfg','w')
cfgFile_Write:write(cfgContent)
io.close(cfgFile_Write)

return
[[
home = E:\Victoria3\V3datas\v3_transfer_tools\python_tools
include-system-site-packages = false
version = 3.10.4
]]