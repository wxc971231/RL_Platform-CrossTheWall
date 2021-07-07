from PyQt5.QtCore import QObject
from core.Util import QABCMeta
import abc

# 策略类的基类，是一个抽象类
# 一般通过设置 metaclass = abc.ABCMeta 定义抽象类，为了避免元类冲突，这里把元类设置为QABCMeta
# 抽象类中，带有 @abc.abstractmethod 注释的方法在实现类中必须重写
class BasePolicy(QObject,metaclass = QABCMeta):
    def __init__(self,controller):
        super().__init__() 
        self.controller = controller
        self.map = controller.map
        self.centralwidget = controller.centralwidget

        self.pi = []            # 策略二维列表
        self.gamma = 0.9        # 折扣系数
        self.alpha = 0.1        # 学习率
        self.epsilon = 0.2      # 试探概率
        self.autoExec = False   # 自动执行
        self.autoThread = None  # 自动执行线程
        self.layout = None
    
    # setter ------------------------------------------------------------------------
    def setGamma(self,gamma):
        self.gamma = gamma

    def setAlpha(self,alpha):
        self.alpha = alpha

    def setEpsilon(self,epsilon):
        self.epsilon = epsilon

    # UI相关 -------------------------------------------------------------------------
    def setLayoutVisiable(self,visible):
        layout = self.controlLayout()
        for i in range(layout.count()):     # 除了上分布spacer其他都设置visible
            layout.itemAt(i).widget().setVisible(visible)

    # 控制 ---------------------------------------------------------------------------
    def initQ(self):
        cubes = self.map.gridWidget.cubes
        map_colum = self.map.gridWidget.colum
        map_row = self.map.gridWidget.row

        for row in range(map_row):
            for colum in range(map_colum):
                cubes[row][colum].Q = {0:0,1:0,2:0,3:0} 
                cubes[row][colum].value = 0  
        
        # 处理边界位置动作集只有两个或三个动作，特殊处理
        cubes[0][0].Q[0] = -10000
        cubes[0][0].Q[2] = -10000
        cubes[0][map_colum-1].Q[0] = -10000
        cubes[0][map_colum-1].Q[3] = -10000
        cubes[map_row-1][0].Q[1] = -10000
        cubes[map_row-1][0].Q[2] = -10000
        cubes[map_row-1][map_colum-1].Q[1] = -10000
        cubes[map_row-1][map_colum-1].Q[3] = -10000

        for row in range(map_row-2):
            cubes[1+row][0].Q[2] = -10000
            cubes[1+row][map_colum-1].Q[3] = -10000
        
        for colum in range(map_colum-2):
            cubes[0][1+colum].Q[0] = -10000
            cubes[map_row-1][1+colum].Q[1] = -10000        

    def initPolicy(self):
        cubes = self.map.gridWidget.cubes
        map_colum = self.map.gridWidget.colum
        map_row = self.map.gridWidget.row

        # 初始化为随机策略，动作价值函数都初始化为0
        self.pi = []
        for row in range(map_row):
            pi_row = []
            for colum in range(map_colum):
                cubes[row][colum].resetPolicy()      
                pi_row.append(cubes[row][colum].pi.copy())
            self.pi.append(pi_row)
                
    def resetPolicy(self):
        self.waitAutoExecEnd()
        self.initPolicy()
        self.map.gridWidget.update()
    
    # 结束策略自动执行子线程
    def waitAutoExecEnd(self):
        self.autoExec = False
        if self.autoThread != None:
            while self.autoThread.is_alive():
                pass

    # 子类方法 -------------------------------------------------------------------------
    # (此方法子类必须重写) 在此创建并返回一个包含策略控制控件的Layout
    @abc.abstractmethod
    def controlLayout(self):
        return self.layout

    # (此方法子类必须重写) 策略控制layout嵌入controller主窗口时调用，在此初始化
    @abc.abstractmethod
    def controlLayoutInit(self):
        pass

    # (此方法子类必须重写) 策略控制layout从controller主窗口移除时调用，在此做收尾处理
    @abc.abstractmethod
    def controlLayoutRemoved(self):
        pass

    # (此方法子类必须重写)  启动或终止自动执行
    @abc.abstractmethod
    def autoToggle(self):
        pass
