from PyQt5 import QtGui, QtCore, QtWidgets
from sklearn.metrics import pairwise
import numpy as np
import math
from core.Util.map import Cube
from core.Util.Function import valueLimit,randomChoice

# 地图网格对象
class GridWidget(QtWidgets.QWidget):
    cubeSelectedSignal = QtCore.pyqtSignal() 
    cubeUpdateSignal = QtCore.pyqtSignal(bool) 

    def __init__(self,row,colum,map):
        super().__init__()
        self.map = map              # 对象引用
        self.row = row              # 行数
        self.colum = colum          # 列数
    
        self.mouse_x = 0            # 当前光标位置
        self.mouse_y = 0

        self.map_x = 0              # 左上角坐标
        self.map_y = 0  
        self.map_zoom = 1           # 放缩
        self.zoomFlag = False
        self.cube_l = 0             # 方格边长
        self.cubeSelected = None    # 当前选中的块（仅用于方格编辑模式）
        self.penSelected = None     # 当前选中的画笔

        self.cubes = []             # 方格二维列表
        self.cubeArray = None       # 方格坐标数组
        self.distanceArray = np.zeros((row,colum,row,colum),dtype='int')   # 距离邻接矩阵

        self.setMouseTracking(True) # 允许鼠标追踪事件
        self.painter = QtGui.QPainter(self)
        
        self.isDrawingMode = False  # 处于绘制模式
        self.showWithColor = True   # 分色显示
        self.showWithValue = False  # 价值分色显示
        self.maxValue = 5           # 价值分色显示使用的最大绝对价值

    # 初始化gridWidget对象，在加载或新建地图时调用
    def initGrid(self,row,colum):
        self.cubeSelected = None
        self.row = row          
        self.colum = colum  

        self.cubes = []
        self.initCubes()
        self.update()

    def initCubes(self):
        for i in range(self.row):
            colum_cubes = []
            for j in range(self.colum):
                cube = Cube(0,0,i,j,0,self.map,self.map.controller.selectedTask)
                colum_cubes.append(cube)
            self.cubes.append(colum_cubes)

        for i in range(self.row):
            for j in range(self.colum):
                cube = self.cubes[i][j]
                cube.storeNeighborCube()
                cube.resetPolicy()

        columArray = np.arange(self.colum)
        rowArray = np.arange(self.row)
        columArray,rowArray = np.meshgrid(columArray,rowArray)
        self.cubeArray = np.vstack([rowArray.ravel(), columArray.ravel()]).T
        self.distanceArray = pairwise.pairwise_distances(self.cubeArray,metric='euclidean').reshape(self.row,self.colum,self.row,self.colum)

    def taskChanged(self,task):
        for i in range(self.row):
            for j in range(self.colum):
                cube = self.cubes[i][j]
                cube.setActions(task)
        self.reStoreAllNeighborCube()

    # 下一个方格及概率
    # 返回 [row,colum] 处执行 action 后转移到的方格及转移概率列表 [(s_,p),...]
    def nextCubeAndProbList(self,row,colum,action):
        cube = self.cubes[row][colum]
        
        # 终点直接回起点
        if cube.isEnd:    
            nextCubes = []
            for cube in self.map.startCubeList:
                nextCubes.append((cube,1/len(self.map.startCubeList)))
            return nextCubes

        if self.map.controller.selectedTask == 'CrossTheWall':
            # 计算转移到的位置
            next_row = row - action
            next_colum = colum + 1
            
            #next_row = valueLimit(next_row,self.row-1,0)
            if next_row < 0 or next_row > self.row-1:
                return []
            
            if next_colum > self.colum-1:
                next_colum = self.colum-1
            elif not self.cubes[next_row][next_colum].isPassable:
                next_colum = colum
            
            # 这里允许顶着墙走导致不动的情况，正常返回方格，否则依概率选择动作时会报错
            #if row == next_row and colum == next_colum:
            #    return []

        elif self.map.controller.selectedTask == 'GridMaze':
            # 上下左右
            temp_colum = [0,0,-1,1] 
            temp_row = [-1,1,0,0]
            
            # 走一步就出地图
            next_row = row + temp_row[action]
            next_colum = colum + temp_colum[action]
            if next_row > self.row-1 or next_row < 0 or next_colum > self.colum-1 or next_colum < 0:
                return []

            # 如果撞墙，不动
            if not self.cubes[next_row][next_colum].isPassable:
                next_row = row
                next_colum = colum
            
            # 偏移处理
            slide = cube.slide
            if slide != [0,0,0,0]:
                for direction in range(len(slide)):
                    #找到偏移的方向
                    if slide[direction] != 0:
                        for i in range(slide[direction]):
                            next_row += temp_row[direction]
                            next_colum += temp_colum[direction]

                            # 如果偏移到终点，停止
                            if self.cubes[next_row][next_colum] in self.map.endCubeList:
                                return [(self.cubes[next_row][next_colum],1)]

                            # 一直偏移直到停在边界或墙壁前
                            if (next_row > self.row-1 or next_row < 0 or next_colum > self.colum-1 or next_colum < 0) or not self.cubes[next_row][next_colum].isPassable:
                                next_row -= temp_row[direction]
                                next_colum -= temp_colum[direction]
                                break
                        break     

        return [(self.cubes[next_row][next_colum],1)]

    # 更新相邻可达方格，地图编辑完成、任务切换时调用
    def reStoreAllNeighborCube(self):
        for r in range(self.row):
            for c in range(self.colum):
                cube = self.cubes[r][c]
                cube.nextCubeDict = {}
                cube.priorCubeDict = {}

        for r in range(self.row):
            for c in range(self.colum):
                cube = self.cubes[r][c]
                cube.storeNeighborCube()
        
        for r in range(self.row):
            for c in range(self.colum):
                cube = self.cubes[r][c]
                cube.resetPolicy()

    # 绘制事件
    def paintEvent(self,event):
        self.painter.begin(self)
        self.paintEvent = event
        self.drawGrid(self.painter)
        self.painter.end()

    # 鼠标点击事件
    def mousePressEvent(self,event):
        if self.map.isVisible and event.buttons() and QtCore.Qt.LeftButton:
            x = event.x()
            y = event.y()

            # 先清除原先的选中标记
            if(self.cubeSelected != None):
                self.cubeSelected.selected = False

            # 判断点击位置
            colum = math.floor((x-self.map_x)/self.cube_l)
            row = math.floor((y-self.map_y)/self.cube_l)
            if colum < 0 or colum > self.colum-1 or row < 0 or row > self.row-1:
                self.cubeSelected = None
                self.cubeSelectedSignal.emit()
            else:
                self.cubeSelected = self.cubes[row][colum]

                # 如果是画笔模式，设置当前cube的画笔和当前选中画笔一致
                if self.isDrawingMode:
                    if self.cubeSelected.penName != self.penSelected:
                        mapSaved = not self.cubes[row][colum].updateWithPen(self.penSelected)
                        self.cubeUpdateSignal.emit(mapSaved)

                # 如果是编辑模式，设置当前cube为选中状态
                else:
                    self.cubeSelected.selected = True
                    self.cubeSelectedSignal.emit()  

            # 更新gridWidget的UI   
            self.update()

    # 鼠标追踪事件
    def mouseMoveEvent(self,event):
        if self.map.isVisible:
            x = event.x()
            y = event.y()
            self.mouse_x = x
            self.mouse_y = y

            if self.isDrawingMode and event.buttons() and QtCore.Qt.LeftButton:
                colum = math.floor((x-self.map_x)/self.cube_l)
                row = math.floor((y-self.map_y)/self.cube_l)

                if colum >= 0 and colum <= self.colum-1 and row >= 0 and row <= self.row-1:
                    self.cubeSelected = self.cubes[row][colum]
                    if self.isDrawingMode:
                        mapSaved = not self.cubes[row][colum].updateWithPen(self.penSelected)
                        self.cubeUpdateSignal.emit(mapSaved)
                        self.update()
        
    # 鼠标滚轮滚动事件
    def wheelEvent(self, event):
        if self.map.isVisible:
            angle = event.angleDelta() / 8  # 返回QPoint对象，为滚轮转过的数值，单位为1/8度
            angleY = angle.y()              # 竖直滚过的距离
            if angleY > 0:
                self.map_zoom += 0.1
            else:  
                self.map_zoom -= 0.1
                if self.map_zoom < 1:
                    self.map_zoom = 1

            self.zoomFlag = True            
            self.update()

    # 绘制地图网格
    def drawGrid(self,painter):
        if self.map.isVisible:
            self.w = self.width()   
            self.h = self.height()  
            
            # 目前光标所在方格坐标,缩放时用作不动点
            if self.cube_l != 0:
                last_colum = math.floor((self.mouse_x-self.map_x)/self.cube_l)
                last_row = math.floor((self.mouse_y-self.map_y)/self.cube_l)
                last_colum = valueLimit(last_colum,self.colum-1,0)
                last_row = valueLimit(last_row,self.row-1,0)
                
            # 以较长边为基础确定方格边长
            if self.colum/self.row >= self.w/self.h:
                self.cube_l = self.map_zoom*self.w/self.colum
            else:
                self.cube_l = self.map_zoom*self.h/self.row
            
            # 缩放比大于1，以鼠标所在方格左上角为不动点缩放；缩放比等于1且继续下滚时，逐渐调整方格区至中部完全显示位置
            if self.map_zoom > 1:
                self.map_x = self.cubes[last_row][last_colum].x - self.cube_l*last_colum
                self.map_y = self.cubes[last_row][last_colum].y - self.cube_l*last_row  
            else:
                if self.colum/self.row >= self.w/self.h:
                    map_y = 0.5*self.h - 0.5*self.row*self.cube_l
                    map_x = 0
                else:
                    map_x = 0.5*self.w - 0.5*self.colum*self.cube_l
                    map_y = 0

                self.map_x = 0.7*self.map_x + 0.3*map_x
                self.map_y = 0.7*self.map_y + 0.3*map_y
            
            # 刷新cubes二维列表并绘制
            for i in range(self.row):
                for j in range(self.colum):
                    self.cubes[i][j].resize(self.map_x+j*self.cube_l,self.map_y+i*self.cube_l,self.cube_l)
                    self.cubes[i][j].draw(painter)

                    if self.map.showPolicyOfSelectedCube and self.map.showEpisodeOfSelectedCube:
                        self.cubes[i][j].visited = False

            # 显示状态动作价值
            if self.map.showQ:
                cube = self.cubeSelected
                if cube != None and cube.isPassable:
                    for a in cube.action:
                        for nc,p in cube.nextCubeDict[a]:
                            if nc != None:
                                # 有转移 cube,a -> nc, 在nc位置显示信息
                                painter.setPen(QtGui.QColor(0,100,100))
                                painter.setFont(QtGui.QFont('微软雅黑', 0.1*cube.l))
                                # 上：q(cube,a)
                                painter.drawText(QtCore.QRect(nc.x+0.1*nc.l,nc.y+0.1*nc.l,0.8*nc.l,0.8*nc.l),QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop ,str(round(cube.Q[a],3)))
                                # 下：distance(cube,nc)
                                painter.drawText(QtCore.QRect(nc.x+0.1*nc.l,nc.y+0.1*nc.l,0.8*nc.l,0.8*nc.l),QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom,str(round(cube.distance(nc),3)))
                                # 左：pi(a|cube)
                                painter.drawText(QtCore.QRect(nc.x+0.1*nc.l,nc.y+0.1*nc.l,0.8*nc.l,0.8*nc.l),QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft,str(round(cube.pi[a],3)))
                                # 右：p(nc|cube,a)
                                painter.drawText(QtCore.QRect(nc.x+0.1*nc.l,nc.y+0.1*nc.l,0.8*nc.l,0.8*nc.l),QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight,str(round(p,3)))

            # 绘制策略
            if self.map.showPolicy:
                painter.setPen(QtGui.QPen(QtGui.QColor(self.map.policyColor), 0.05*self.cubes[0][0].l, QtCore.Qt.SolidLine)) 
                
                # 绘制选中方格策略
                if self.map.showPolicyOfSelectedCube:
                    # 显示下一步策略
                    if not self.map.showEpisodeOfSelectedCube:
                        cube = self.cubeSelected
                        '''
                        # 所有上一步可达
                        if cube != None:
                            for pc in cube.priorCubeDict:
                                painter.setPen(QtGui.QPen(QtGui.QColor(self.map.policyColor), 0.05*self.cubes[0][0].l, QtCore.Qt.SolidLine)) 
                                painter.drawLine(cube.centerX, cube.centerY, pc.centerX, pc.centerY)

                                painter.setPen(QtGui.QPen(QtGui.QColor(80,80,80), 0.1*self.cubes[0][0].l, QtCore.Qt.SolidLine)) 
                                painter.drawPoint(pc.centerX,pc.centerY)
                        '''
                        # 所有下一步可达
                        if cube != None and cube not in self.map.endCubeList and cube.isPassable:                            
                            for a in cube.action:
                                if cube.pi[a] != 0:
                                    for nc,p in cube.nextCubeDict[a]:
                                        if nc != None:
                                            # 在下一个方块中心画一个点
                                            painter.setPen(QtGui.QPen(QtCore.Qt.black, 0.1*cube.l, QtCore.Qt.SolidLine)) 
                                            painter.drawPoint(nc.centerX, nc.centerY) 
                                            # 连线
                                            painter.setPen(QtGui.QPen(QtGui.QColor(self.map.policyColor), 0.05*self.cubes[0][0].l, QtCore.Qt.SolidLine)) 
                                            painter.drawLine(cube.centerX, cube.centerY, nc.centerX, nc.centerY)

                                            # 如果不显示Q，显示一下pi概率
                                            if not self.map.showQ:
                                                painter.drawText(QtCore.QRect(nc.x+0.1*nc.l,nc.y+0.1*nc.l,0.8*nc.l,0.8*nc.l),QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop ,str(round(cube.pi[a],3)))
                        
                    # 显示此格开始的所有可能轨迹(BFS)
                    else:
                        if self.cubeSelected != None and self.cubeSelected.isPassable:
                            nextCubeQueue = []
                            nextCubeQueue.append(self.cubeSelected)
                            
                            while nextCubeQueue != []:
                                cube = nextCubeQueue[0]
                                if cube not in self.map.endCubeList:
                                    for a in cube.action:
                                        if cube.pi[a] != 0:
                                            for nc,p in cube.nextCubeDict[a]:
                                                if nc != None:
                                                    painter.setPen(QtGui.QPen(QtGui.QColor(self.map.policyColor), 0.05*self.cubes[0][0].l, QtCore.Qt.SolidLine)) 
                                                    painter.drawLine(cube.centerX, cube.centerY, nc.centerX, nc.centerY)
                                                    if not nc.visited:
                                                        nextCubeQueue.append(nc)
                                                        nc.visited = True
                                                        
                                                        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0.1*cube.l, QtCore.Qt.SolidLine)) 
                                                        painter.drawPoint(nc.centerX, nc.centerY) 

                                nextCubeQueue.remove(cube)

                # 绘制全部策略                
                else:
                    for i in range(self.row):
                        for j in range(self.colum):
                            cube = self.cubes[i][j]    
                            if cube.isPassable and cube not in self.map.endCubeList:
                                for a in cube.action:
                                    if cube.pi[a] != 0:
                                        for nc,p in cube.nextCubeDict[a]:
                                            if nc != None:
                                                painter.drawLine(cube.centerX, cube.centerY, nc.centerX, nc.centerY)
            
    # 获取当前总价值
    def getSumValue(self):
        v = 0
        for row in range(self.row):
            for colum in range(self.colum):
                if self.cubes[row][colum].isPassable:
                    v += self.cubes[row][colum].value
        return v
