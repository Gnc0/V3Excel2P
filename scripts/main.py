import os
import sys
import pandas as pd

def GetCondition(_string):
    #如果是索引，则跳过列
    if _string == 'index':
        return 'note'
    #如果是备注，则跳过该列
    if 'note' in _string:
        return 'note'
    #如果是逗号和点号，则可能是table或者array
    if ',' in _string or '.' in _string:
        if ',' in _string:
            _string += 'table'
        if '.' in _string:
            _string += 'array'
        return _string
    #如果都不是，正常转换
    return 'normal'

def AddString(_title,_content):
    return '\t%s = %s\n'%(_title,_content)

def IfNotSpace(title,content):
    #检测空行
    if content != 'nan' and title != 'nan':
        return True
    else:
        return False




def ConvertSheetToDict(df,sheetName):
    #字段索引列表
    titleList = df.values.tolist()[1]
    #中文备注索引列表
    #noteList = df.values.tolist()[2] 
    #数据格式列表
    #formatList = df.values.tolist()[n]
    #content矩阵
    contentMatrix = df.values.tolist()[3:]
    #content字典
    contentDict = dict()
    #遍历每一行
    for contentList in contentMatrix:
        #
        index = str(contentList[0])
        if contentList[0] == 'nan':
            continue
        contentDict[index] = dict()
        #获取一共多少列
        column,columnMax = 0,len(titleList)
        #遍历列
        while column < columnMax:
            #标题列
            title = str(titleList[column])
            #内容列
            content = str(contentList[column])
            #查看标题和内容
            #print(title,content)
            #确定处理方式
            condition = GetCondition(title)
            #如果处理为数组
            if 'table' in condition:
                #如果有点号，则添加对应的字典层级
                if 'array' in condition:
                    hierachies = title.split('.')
                    title = hierachies[-1:][0]
                    #ReadHierachy(contentDict[index],hierachies)
                #拆开array字段获取长度和宽度
                array = title.split(',')
                arrayName,arrayLength,arrayDepth = str(array[0]),int(array[1]),int(array[2])
                #如果是value和type
                if arrayDepth == 2:
                    #开头
                    hierachy = dict()
                    #
                    column += 1
                    for pos in range(arrayLength):
                        #确保column不会溢出
                        if column >= columnMax:
                            break
                        #设置title和content
                        title_1 = str(titleList[column])
                        content_1 = str(contentList[column])
                        #判断是否仍然在数组
                        if title_1 != 'type' and title_1 != 'value':
                            break
                        #遍历下一列
                        column += 1
                        #设置tilte和content
                        title_2 = str(titleList[column])
                        content_2 = str(contentList[column])
                        #检查type、value以及空行
                        if title_1 == 'type' and title_2 == 'value' and IfNotSpace(content_1,content_2):
                            hierachy[content_1] = content_2
                        #遍历下一列
                        column += 1
                    column -= 1
                #如果只有value
                if arrayDepth == 1:
                    column += 1
                    hierachy = list()
                    for pos in range(arrayLength):
                        #确保column不会溢出
                        if column >= columnMax:
                            break
                        #设置title和content
                        title_1 = str(titleList[column])
                        content_1 = str(contentList[column])
                        #判断是否仍在数组
                        if title_1 != 'value':
                            break
                        #检查value以及空行
                        if title_1 == 'value' and IfNotSpace(title_1,content_1):
                            hierachy.append('\t\t%s\n'%content_1)
                        column += 1
                    column -= 1
                #是否存在多维数组层级
                if 'array' in condition:
                    #存在则添加多维数组层级
                    #给hierachies加arrayName
                    hierachies.pop(-1)
                    hierachies.append(arrayName)
                    AddHierachy(contentDict[index],hierachies,hierachy)
                else:
                    #不存在则正常添加层级
                    if arrayDepth == 2:
                        contentDict[index][arrayName] = hierachy
                    if arrayDepth == 1:
                        contentDict[index][arrayName] = hierachy
            if condition == 'array':
                None
            #如果没有特殊处理而且不是空行
            if condition == 'normal' and IfNotSpace(title,content):
                #写一行
                contentDict[index][title] = content
            #下一列
            column += 1
    return contentDict

def AddHierachy(hierachyDict,hierachies,hierachy):
    if hierachies[0] in list(hierachyDict.keys()):
        if len(hierachies) == 1:
            if len(hierachy) == 0:
                return None
            hierachyDict[hierachies[0]] = hierachy
            return hierachyDict
        hierachyDict = AddHierachy(hierachyDict[hierachies[0]], hierachies[1:],hierachy)
    else:
        if len(hierachies) == 1:
            if len(hierachy) == 0:
                return None
            hierachyDict[hierachies[0]] = hierachy
            return hierachyDict
        hierachyDict[hierachies[0]] = dict()
        hierachyDict = AddHierachy(hierachyDict[hierachies[0]], hierachies[1:],hierachy)
    return hierachyDict
       
def GetStringDictionary(df):
    #字段索引列表
    titleList = df.values.tolist()[1]
    #中文备注索引列表
    #noteList = df.values.tolist()[2] 
    #数据格式列表
    #formatList = df.values.tolist()[n]
    #content矩阵
    contentMatrix = df.values.tolist()[3:]
    #content字典
    stringDict = dict()
    for contentList in contentMatrix:
        index = str(contentList[0])
        if contentList[0] == 'nan':
            continue
        #获取一共多少列
        column,columnMax = 0,len(titleList)
        #遍历列
        while column < columnMax :
            #标题列
            title = str(titleList[column])
            #如果title是value
            if title == 'value':
                #内容列
                content = str(contentList[column])
                #赋值
                stringDict[index] = content
            column += 1
    return stringDict
    
def FourSpace(level):
    s = ''
    for i in range(level):
        s += '\t'
    return s

class Reader():
    
    def __init__(self,sheetName,stringDict,):
        self.txt = '# sheet is %s\n'%sheetName
        self.stringDict = stringDict
        self.stringList = list(stringDict.keys())

    def IfInStringDictionary(self,s):
        #如果在字符串字典中，则修改文本
        if s in self.stringList:
            return self.stringDict[s]
        return s


    def ReadContentDictValue(self,level,key,value):
        level += 1
        #如果是字典
        if (type(value)) == type(dict()):
            for _value in list(value.keys()):
                #判断是不是字符串
                if type(value[_value]) == type(dict()):
                     #如果不是字符串，判断字典长度
                    if len(value[_value]) > 0:
                        #如果字典长度大于0，则递归
                        key1 = self.IfInStringDictionary(_value)
                        value1 = self.IfInStringDictionary(value[_value])
                        self.txt += '%s%s = {\n'%(FourSpace(level),key1)
                        self.ReadContentDictValue(level,key1,value1)
                        self.txt += '%s}\n'%(FourSpace(level))
                elif type(value[_value]) == type([]):
                    #直接添加list的元素
                    self.txt += '%s%s = {\n'%(FourSpace(level),_value)
                    for element in value[_value]:
                        element = self.IfInStringDictionary(element)
                        self.txt += '%s%s'%(FourSpace(level-2),element)
                    self.txt += '%s}\n'%(FourSpace(level))
                elif type(value[_value]) == type(''):
                   #是字符串，直接赋值
                    key1 = self.IfInStringDictionary(_value)
                    value1 = self.IfInStringDictionary(value[_value])
                    self.txt += '%s%s = %s\n'%(FourSpace(level),key1,value1)
        elif type(value) == type([]):
            #直接添加list的元素
            for element in value:
                element = self.IfInStringDictionary(element)
                self.txt += '%s%s'%(FourSpace(level-2),element)
        elif type(value) == type(''):
            #直接添加字符串
            key = self.IfInStringDictionary(key)
            value = self.IfInStringDictionary(value)
            self.txt += '%s%s = %s\n'%(FourSpace(level),key,value)
        return key,value

if __name__ == '__main__':
    #=============================



    #=============================
    try:
        rootPath = sys.argv[1] #获得根路径
    except IndexError:
        print('找不到目录')
    
    print('=====进入python=====')
    print("当前python版本: ", sys.version)
    
    #修正根目录丢失'\'的可能错误
    if rootPath[-1:] != '\\':
        rootPath = rootPath + '\\'
    #获得excel的路径
    excelPath = rootPath + 'excel\\'
    #获得txt的路径
    txtPath = rootPath + 'txt\\'
    #提示各种目录
    print('========目录========')
    print('当前excel目录：%s'%excelPath)
    print('当前的txt目录：%s'%txtPath)
    print('========进度========')
    #获得excel路径下所有文件
    stream = os.listdir(excelPath) 
    
    #声明可用后缀条件列表
    condition_suffix = ['.xlsx','.xlsm']
    
    #声明不可用后缀条件列表
    condition_ban = dict() 
    condition_ban['.xls'] = '警告：只能使用.xlsx后缀，最好不要使用.xls后缀'
    
    #声明excel文件的列表
    fileList = list() 
    #遍历excel路径下的所有文件，获取待处理文件
    for file in stream:
        ifAppendFile = True
        #可用后缀
        if file[-5:] not in condition_suffix: 
            ifAppendFile = False
        #不可用后缀
        if file[-4:] in condition_ban.keys(): 
            ifAppendFile = False
            print(condition_ban[file[-4:0]])
        #不读取被打开的excel文件
        if file[:2] == '~$':
            ifAppendFile = False
            print('警告：检测到可能有正在打开的excel文件，这可能导致转表失败，请查验\n')
        if file[:1] == '!':
            ifAppendFile = False
            print('跳过 ! 开头的文件：'+str(file)+'\n')
        if ifAppendFile:
            fileList.append(file)
    #特殊处理的列表，暂无开发
    specialSheet = []
    #处理所有符合条件的excel文件
    for file in fileList:
        #打印处理excel的信息
        print('处理excel：%s'%file ) 
        #获取sheet
        _sheetList = list(pd.read_excel('%s\\%s'%(excelPath,file),sheet_name=None).keys()) 
        #声明sheetList
        sheetList = list() 
        #sheetList赋值
        for i in range(len(_sheetList)): 
            if _sheetList[i] == 'string_dictionary':
                #打印处理sheet的信息
                print('--处理sheet：%s.txt'%_sheetList[i]) 
                #初始化DataFrame
                df = pd.DataFrame(pd.read_excel('%s\\%s'%(excelPath,file),sheet_name=_sheetList[i],header=None))
                #转stringDict表
                stringDict = GetStringDictionary(df)
                #print(stringDict)
                continue
            if 'note' not in _sheetList[i]:
                sheetList.append(_sheetList[i])
        #遍历每个sheet
        for sheet in sheetList:
            #打印处理sheet的信息
            print('--处理sheet：%s.txt'%sheet) 
            #初始化DataFrame
            df = pd.DataFrame(pd.read_excel('%s\\%s'%(excelPath,file),sheet_name=sheet,header=None))
            #处理sheet
            contentDict = ConvertSheetToDict(df,sheet)
            #
            reader = Reader(sheet,stringDict)
            reader.ReadContentDictValue(-1,'',contentDict)
            #写入文件
            with open( '%s%s.txt'%(txtPath,sheet),'w', encoding='utf-8') as f:
                f.write(reader.txt)
            """
            if sheet in specialSheet:
                None
            """
        #打印间隔
        print('\n')

    print('=====退出python=====')





