import os
import numpy as np
import json
from core.Util import WaveData

class WaveFile():
    def __init__(self):
        self.__head = 'This is the policy data file for figure generator, do not modify it manually'   
        self.__version = 'v1.1' 
        self.returnList = []
        self.lengthList = []
        self.fileName = ''    
        self.filePath = ''    
        
    # 把map配置文件存储到filePath路径, 使用json形式存储波形文件              
    def saveWave(self,wave):
        self.returnList = list(wave.returnArray)
        self.lengthList = list(wave.lengthArray)
        filePath = wave.path

        #如果有同名文件，删除原来的
        if os.access(filePath, os.F_OK):
            os.remove(filePath)

        with open(filePath, 'w') as file:
            waveJson = json.dumps(self.__dict__)
            file.write(waveJson)

    def loadWave(self,filePath):
        text = 'Loading wave：'+filePath[filePath.rfind('/')+1:]+'...\n'
        text += '-'*50+'\n    '
        if filePath[-3:] != '.wd':
            return text + 'Failed! 文件类型错误！请选择.wd文件',None

        with open(filePath, 'r', encoding='UTF-8') as file:
            try:
                lines = file.readlines()
                self.__dict__ = json.loads(lines[0])
            except Exception as e:
                return text + 'Failed! '+str(e),None

        # 判断标记
        if self.__head != 'This is the policy data file for figure generator, do not modify it manually':
            return text + 'Failed! 文件标识错误!',None
        elif self.__version != 'v1.1':
            return text + 'Failed! UI版本错误！',None
        
        waveData = WaveData(np.array(self.returnList),np.array(self.lengthList))
        waveData.name = self.fileName = filePath[filePath.rfind('/')+1:-3]
        waveData.path = self.filePath = filePath

        return text + 'Success!',waveData