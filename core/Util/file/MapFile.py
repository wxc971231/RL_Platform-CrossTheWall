import os
from core.Util.map import Pen,Cube

class MapFile():
    def __init__(self):
        self.__head = 'This is the map data file for map editor, do not modify it manually'   
        self.__version = 'v1.0'     
        self.fileName = ''    
        self.filePath = ''                        
            
    # 把map配置文件存储到filePath路径              
    def saveMap(self,filePath,map):
        #如果有同名文件，删除原来的
        if os.access(filePath, os.F_OK):
            os.remove(filePath)

        # 开始写入文件
        fp = open(filePath,'w') 
        fp.write(self.__head+'\n\n')
        
        # UI版本
        fp.write('UI version:'+self.__version+'\n\n')
        
        # 画笔参数
        fp.write('Pen para:\n')
        for penName in map.penDict:
            pen = map.penDict[penName]
            fp.write('{0},{1},{2},{3};{4},{5},{6},{7}\n'.format(pen.name,pen.color,pen.reward,pen.isPassable,*(pen.slide)))
        fp.write('\n')
        
        # 地图参数
        fp.write('map para:\n')
        fp.write('{0},{1}\n'.format(map.gridWidget.row,map.gridWidget.colum))
        
        if map.startCube == None: 
            fp.write('None\n')
        else:
            fp.write('{0},{1}\n'.format(map.startCube.row,map.startCube.colum))
            
        if map.endCube == None: 
            fp.write('None\n')
        else:
            fp.write('{0},{1}\n'.format(map.endCube.row,map.endCube.colum))
        fp.write(str(map.disCostDiscount)+'\n')

        fp.write('\n')
        
        # 方块参数
        fp.write('Cubes para:\n')
        for i in range(map.gridWidget.row):
            for j in range(map.gridWidget.colum):
                cube = map.gridWidget.cubes[i][j]
                fp.write('{0},{1},{2},{3},{4},{5},{6};{7},{8},{8},{10}\n'.format(*(cube.row,cube.colum,cube.reward,cube.penName,
                                                             str(cube.isPassable),str(cube.isStart),str(cube.isEnd),*(cube.slide))))
        fp.write('\n')

        # 结束标记
        fp.write('end')
        fp.close()

        self.fileName = filePath[filePath.rfind('/')+1:-4]
        self.filePath = filePath

    # 加载地图
    def loadMap(self,filePath,map):
        if filePath[-4:] != '.txt':
            return '文件类型错误！请选择.txt文件'

        # 读取文件
        with open(filePath,'r') as fp:
            lines = fp.readlines()

            # 初步判断标记
            if lines[0] != 'This is the map data file for map editor, do not modify it manually\n':
                return '配置文件格式错误：文件标识错误!'
            elif lines[2] != 'UI version:v1.0\n':
                return '配置文件格式错误：UI版本错误！'
            elif lines[4] != 'Pen para:\n':
                return '配置文件格式错误：未检测到画笔参数标识！'
            elif lines[-1] != 'end':
                return '配置文件格式错误：未检测到结束标识！'

            # 开始加载数据
            else:
                # 备份当前数据，加载失败时用于恢复
                penDictBackup = map.penDict.copy()
                rowBackup = map.gridWidget.row
                columBackup = map.gridWidget.colum
                stepRewardBackup = map.disCostDiscount
                if map.startCube != None:
                    startCubeBackup = map.startCube.copy()
                else:
                    startCubeBackup = None

                if map.endCube != None:
                    endCubeBackup = map.endCube.copy()
                else:
                    endCubeBackup = None                

                # 加载画笔
                num = 0
                try:
                    map.penDict.clear()
                    while lines[5+num] != '\n':
                        line = lines[5+num]
                        slidePos = line.find(';')
                        para = line[:slidePos].split(',')
                        slide = line[slidePos+1:].split(',')
                        
                        for i in range(4):
                            slide[i] = int(slide[i])

                        map.penDict[para[0]] = Pen(para[1],para[0],slide,para[3] == 'True',float(para[2]))
                        num = num+1
                except Exception as e:
                    print(e)
                    map.penDict = penDictBackup
                    return '画笔数据加载失败'

                # 加载地图配置参数
                num = num+1
                if lines[5+num] != 'map para:\n':
                    return '配置文件格式错误：未检测到地图配置参数标识！'
                else:
                    startCubePos = [-1,-1]
                    endCubePos = [-1,-1]
                    try:
                        size = lines[5+num+1].split(',')
                        map.gridWidget.row = int(size[0])
                        map.gridWidget.colum = int(size[1])
                        
                        if lines[5+num+2] == 'None\n':
                            map.startCube = None
                        else:
                            startCubePos[0] = int(lines[5+num+2].split(',')[0])
                            startCubePos[1] = int(lines[5+num+2].split(',')[1])
                        
                        if lines[5+num+3] == 'None\n':
                            map.endCube = None
                        else:
                            endCubePos[0] = int(lines[5+num+3].split(',')[0])
                            endCubePos[1] = int(lines[5+num+3].split(',')[1])

                        map.disCostDiscount = float(lines[5+num+4])
                    except Exception as e:
                        print(e)
                        map.penDict = penDictBackup
                        map.gridWidget.row = rowBackup
                        map.gridWidget.colum = columBackup
                        map.startCube = startCubeBackup
                        map.endCube = endCubeBackup
                        map.disCostDiscount = stepRewardBackup
                        return '地图配置参数加载失败'

                    # 加载方格数据
                    num = num+6
                    if lines[5+num] != 'Cubes para:\n':
                        return '配置文件格式错误：未检测到方格参数标识！'
                    else:
                        newCubes = []
                        for i in range(map.gridWidget.row):
                            colum_cubes = []
                            for j in range(map.gridWidget.colum):
                                cube = Cube(0,0,i,j,0,map)
                                colum_cubes.append(cube)
                            newCubes.append(colum_cubes)

                        try:
                            num = num+1
                            while lines[5+num] != '\n':
                                line = lines[5+num]
                                slidePos = line.find(';')
                                para = line[:slidePos].split(',')
                                slide = line[slidePos+1:].split(',')
                                for i in range(4):
                                    slide[i] = int(slide[i])
                                
                                row = int(para[0])
                                colum = int(para[1])
                                cube = newCubes[row][colum]
                                cube.reward = float(para[2])
                                cube.penName = para[3]
                                cube.isPassable = (para[4] == 'True')
                                cube.isStart = (para[5] == 'True')
                                cube.isEnd = (para[6] == 'True')
                                cube.slide = slide

                                num = num+1
                        except Exception as e:
                            print(e)
                            map.penDict = penDictBackup
                            map.gridWidget.row = rowBackup
                            map.gridWidget.colum = columBackup
                            map.startCube = startCubeBackup
                            map.endCube = endCubeBackup
                            map.disCostDiscount = stepRewardBackup
                            return '方格数据加载失败'

                        map.gridWidget.cubes = newCubes
                        if startCubePos[0] != -1:
                            map.startCube = newCubes[startCubePos[0]][startCubePos[1]]
                        if endCubePos[0] != -1:
                            map.endCube = newCubes[endCubePos[0]][endCubePos[1]]

        self.fileName = filePath[filePath.rfind('/')+1:-4]
        self.filePath = filePath
        map.saved = True
        map.gridWidget.initCubes()
        return '加载成功'     