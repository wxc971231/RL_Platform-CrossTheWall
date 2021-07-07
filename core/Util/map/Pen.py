# 手动绘制地图时使用的属性画笔对象
class Pen():
    def __init__(self,color,name,slide,isPassable,reward):    
        self.color = color
        self.name = name  
        self.slide = slide  
        self.isPassable = isPassable  
        self.reward = reward     

    def initByCube(self,cube):       
        self.slide = cube.slide
        self.isPassable = cube.isPassable  
        self.reward = cube.reward    