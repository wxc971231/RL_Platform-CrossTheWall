# 手动绘制地图时使用的属性画笔对象
class Pen():
    def __init__(self,color,name,slide,isPassable,isStart,isEnd,reward):    
        self.name = name  
        self.color = color
        self.reward = reward   
        self.isPassable = isPassable   
        self.isStart = isStart
        self.isEnd = isEnd
        self.slide = slide  
        
    def initByCube(self,cube):       
        self.slide = cube.slide
        self.isPassable = cube.isPassable  
        self.isStart = cube.isStart
        self.isEnd = cube.isEnd
        self.reward = cube.reward  

    def updatePen(self,color,name,slide,isPassable,isStart,isEnd,reward):
        self.name = name  
        self.color = color
        self.reward = reward   
        self.isPassable = isPassable   
        self.isStart = isStart
        self.isEnd = isEnd
        self.slide = slide  

    def __eq__(self, other):        
        if type(other) == type(self) and \
            other.name == self.name and \
            other.color == self.color and \
            other.reward == self.reward and \
            other.isPassable == self.isPassable and \
            other.isStart == self.isStart and \
            other.isEnd == self.isEnd and \
            other.slide == self.slide:
            return True
        else:
            return False
