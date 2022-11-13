import os
import sys
import pandas as pd

def isBlankSpace(title,content):
    #检测空行
    if title == 'nan' or content == 'nan':
        return True
    else:
        return False

def ConvertSheetToContentDict(df,sheetName):
    # 字段索引列表
    titleList = df.values.tolist()[1]
    # 中文备注索引列表
    # noteList = df.values.tolist()[2] 
    # 数据格式列表
    # formatList = df.values.tolist()[n]
    # content矩阵
    contentMatrix = df.values.tolist()[3:]
    # content字典
    contentDict = dict()
    # 遍历每一行和每一列
    for contentList in contentMatrix:
        index = str(contentList[0])
        if index == 'nan':
            continue
        contentDict[index] = dict()
        # 遍历该行的每一列
        column,columnMax = 1,len(titleList)
        while column < columnMax:
            # 获取列的标题和内容
            title = str(titleList[column])
            content = str(contentList[column])
            hierachies = ''
            # 是否存在层级
            if '.' in title:
                hierachies = title.split('.')
                title = hierachies[-1:][0]
            # 是否为多维数组
            if ',' in title:
                # 拆开array字段获取长度和宽度
                array = title.split(',')
                arrayName,arrayLength,arrayDepth = str(array[0]),int(array[1]),int(array[2])
                # 如果是type和value形式的
                if arrayDepth == 2:
                    hierachy = dict()
                    column += 1
                    for pos in range(arrayLength):
                        # 确保column不会溢出
                        if column >= columnMax:
                            break
                        # 设置type的title和content
                        type_title = str(titleList[column])
                        type_content = str(contentList[column])
                        # 如果不在数组，就退出数组
                        if type_title != 'type':
                            print(f'【错误】：{index}第{column}列的字段应为\"type\"')
                            break
                        # 设置value的title和content
                        column += 1
                        value_title = str(titleList[column])
                        value_content = str(contentList[column])
                        # 如果不在数组，就退出数组
                        if value_title != 'value':
                            print(f'【错误】：{index}第{column}列的字段应为\"value\"')
                            break
                        # 检查type、value以及空行
                        if not isBlankSpace(type_content,value_content):
                            hierachy[type_content] = value_content
                        column += 1
                    column -= 1
                # 如果只有value
                if arrayDepth == 1:
                    hierachy = list()
                    column += 1
                    for pos in range(arrayLength):
                        # 确保column不会溢出
                        if column >= columnMax:
                            break
                        # 设置title和content
                        value_title = str(titleList[column])
                        value_content = str(contentList[column])
                        #判断是否仍在数组
                        if value_title != 'value':
                            print(f'【错误】：{index}第{column}列的字段应为\"value\"')
                            break
                        #检查value以及空行
                        if value_title == 'value' and not isBlankSpace(value_title,value_content):
                            hierachy.append(f'{value_content}')
                        column += 1
                    column -= 1
                # 是否存在多维数组层级
                if isinstance(hierachies,list):
                    # 存在则添加多维数组层级
                    hierachies.pop(-1)
                    hierachies.append(arrayName)
                    AddHierachy(contentDict[index],hierachies,hierachy)
                else:
                    # 不存在则正常添加层级
                    contentDict[index][arrayName] = hierachy
            # 检查hierachies
            elif isinstance(hierachies,list) and not isBlankSpace(title,content):
                AddHierachy(contentDict[index],hierachies,content)     
            #如果没有特殊处理而且不是空行，写一行
            elif 'note' not in title and not isBlankSpace(title,content):
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
    
# 添加水平制表符\t
def AddHorizontalTab(level):
    s = ''
    for i in range(level):
        s += '\t'
    return s

class Reader():
    
    def __init__(self,):
        self.txt = ''
        
        self.stringReplaceDictKeys = list()
        self.stringReplaceDict = dict()
        
        self.contentDict = dict()
        self.sheetList = list()
        
        self.english = 'l_english:\n'
        self.simp_chinese = 'l_simp_chinese:\n'

    def GetStringReplaceDict(self,df):
        # 字段索引列表
        titleList = df.values.tolist()[1]
        # content矩阵
        contentMatrix = df.values.tolist()[3:]
        # 遍历contentMatrix的每一行和每一列
        for contentList in contentMatrix:
            # 声明table名称index
            index = str(contentList[0])
            value = str(contentList[1])
            # 如果碰到index为空，则跳过到下一行
            if index == 'nan':
                continue
            # 赋值
            self.stringReplaceDict[index] = value
            # 遍历当前行的每一列，用于本地化
            for column in range(len(titleList)):
                title = str(titleList[column])
                content = str(contentList[column])
                if title == 'localization_english' and content != 'nan':
                    self.english += f' {value}:0 \"{content}\"\n'
                if title == 'localization_simp_chinese' and content != 'nan':
                    self.simp_chinese += f' {value}:0 \"{content}\"\n'
        self.stringReplaceDictKeys = list(self.stringReplaceDict.keys())
    
    def Localization(self,name):
        # 写入文件，以utf-8 with BOM的编码方式
        with open( f'{localPath}\\{name}_100_l_english.yml','w', encoding='utf_8_sig') as f:
            f.write(self.english)
        with open( f'{localPath}\\{name}_100_l_simp_chinese.yml','w', encoding='utf_8_sig') as f:
            f.write(self.simp_chinese)
    
    #如果在字符串替代字典中，则修改文本
    def isReplacable(self,s):
        if s in self.stringReplaceDictKeys:
            return self.stringReplaceDict[s]
        return s
    # 阅读列表
    def ReadList(self,htLevel,thisKey,thisValue):
        if len(thisValue) > 0:
            self.txt += f'{AddHorizontalTab(htLevel)}{thisKey}'+' = {\n'
            for element in thisValue:
                element = self.isReplacable(element)
                self.txt += f'{AddHorizontalTab(htLevel)}\t{element}\n'
            self.txt += f'{AddHorizontalTab(htLevel)}'+'}\n'
    # 阅读字符串
    def ReadStr(self,htLevel,thisKey,thisValue):
        thisKey = self.isReplacable(thisKey)
        thisValue = self.isReplacable(thisValue)
        self.txt += f'{AddHorizontalTab(htLevel)}{thisKey} = {thisValue}\n'
    # 阅读字典
    def ReadDict(self,htLevel,thisKey,thisValue):
        if len(thisValue) > 0 and thisKey != '':
            self.txt += f'{AddHorizontalTab(htLevel)}{thisKey} = ' + '{\n'
            htLevel += 1
        for nextKey in list(thisValue.keys()):
            nextValue = thisValue[nextKey]
            if isinstance(nextValue,dict):
                if len(nextValue) > 0:
                    _key = self.isReplacable(nextKey)
                    _value = self.isReplacable(thisValue[nextKey])
                    htLevel -= 1
                    self.ReadContentDictValue(htLevel,_key,_value)
                    htLevel += 1
            elif isinstance(nextValue,list):
                self.ReadList(htLevel,nextKey,nextValue)
            elif isinstance(nextValue,str):
                self.ReadStr(htLevel,nextKey,nextValue)
        if len(thisValue) > 0 and thisKey != '':
            htLevel -= 1
            self.txt += f'{AddHorizontalTab(htLevel)}' + '}\n'
        
    # 阅读sheet内容
    def ReadContentDictValue(self,htLevel,thisKey,thisValue):
        htLevel += 1
        if isinstance(thisValue,dict):
            self.ReadDict(htLevel,thisKey,thisValue)            
        elif isinstance(thisValue,list):
            self.ReadList(htLevel,thisKey,thisValue)
        elif isinstance(thisValue,str):
            self.ReadStr(htLevel,thisKey,thisValue)
        return thisKey,thisValue

if __name__ == '__main__':
    try:
        rootPath = sys.argv[1] #获得根路径
    except IndexError:
        print('找不到目录')
    
    print('=====进入python=====')
    print("当前python版本: ", sys.version)
    
    # 修正根目录丢失'\'的可能错误
    if rootPath[-1:] != '\\':
        rootPath = rootPath + '\\'
    # 获得excel和txt的路径
    excelPath = rootPath + 'excel\\'
    commonPath = rootPath + 'excel\\common\\'
    localPath = rootPath + 'excel\\localization\\'
    # 如果没有目录就创建目录
    if not os.path.exists(commonPath):
        os.mkdir(commonPath)
    if not os.path.exists(localPath):
        os.mkdir(localPath)
    #提示各种目录
    print('========目录========')
    print(f'当前excel目录：{excelPath}')
    print(f'当前的common目录：{commonPath}')
    
    print('========进度========')
    #获得excel路径下所有文件
    stream = os.listdir(excelPath) 
    
    #声明可用后缀条件列表
    suffix_permit = ['.xlsx','.xlsm']

    #声明excel文件的列表
    fileList = list() 
    #遍历excel路径下的所有文件，获取待处理文件
    for file in stream:
        #检测不可用后缀
        if '.xls' in file and '.xlsm' not in file:
            print('【警告】只能使用.xlsx后缀，不要使用.xls后缀')
            continue
        elif '~$' in file:
            print('【警告】检测到可能有正在打开的excel文件，这可能导致转表失败，请查验')
            continue
        elif '!' in file:
            print(f'【提示】跳过包含\"!\"的文件：{file}')
            continue
        # 检测是否包含可用后缀，如果有，加入fileList
        for suffix in suffix_permit:
            if suffix in file:
                fileList.append(file)
            
    # 特殊处理的列表，暂无开发
    specialSheet = []
    
    # 处理所有符合条件的excel文件
    for file in fileList:
        print(f'处理excel：{file}' ) 
        # 声明reader
        reader = Reader()
        # 声明sheetList
        sheetList = list(pd.read_excel(f'{excelPath}\\{file}',sheet_name=None).keys())
        # 剔除note sheet;处理string_dictionary sheet
        for index in range(len(sheetList)):
            if sheetList[index] == 'string_dictionary':
                print(f'--处理sheet：{sheetList[index]}.txt') 
                # 初始化DataFrame
                df = pd.DataFrame(pd.read_excel(f'{excelPath}\\{file}',sheet_name=sheetList[index],header=None))
                # 初始化stringReplaceDict
                reader.GetStringReplaceDict(df)
                # 生成本地化文本
                localName = str(df.values.tolist()[0][0])[9:]
                reader.Localization(localName)
            elif 'note' not in sheetList[index]:
                reader.sheetList.append(sheetList[index])
        # 遍历每个sheet
        for sheet in reader.sheetList:
            reader.txt = ''
            # 初始化DataFrame
            df = pd.DataFrame(pd.read_excel(f'{excelPath}\\{file}',sheet_name=sheet,header=None))
            address = str(df.values.tolist()[0][0])[8:]
            print(f'--处理sheet：{address}\\{sheet}.txt')
            if address == '':
                print(f'【警告】未找到{sheet}的文件夹地址，会直接生成在common文件夹下')
            # 处理sheet
            reader.contentDict = ConvertSheetToContentDict(df,sheet)
            # 阅读contentDict
            reader.ReadContentDictValue(-1,'',reader.contentDict)
            # 写入文件，以utf-8 with BOM的编码方式
            if not os.path.exists(commonPath+address):
                os.mkdir(commonPath+address)
            with open( f'{commonPath}{address}\\{sheet}.txt','w', encoding='utf_8_sig') as f:
                f.write(reader.txt)
    print('=====退出python=====')





