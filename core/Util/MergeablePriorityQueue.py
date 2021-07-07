# 去重优先队列(用于优先级规划)
class MergeablePriorityQueue():
    def __init__(self):
        self.queue = {}
        self.len = 0

    def enQueue(self,obj,p):
        if obj not in self.queue:
            self.queue[obj] = 0
        if self.queue[obj] == 0:
            self.len += 1
        self.queue[obj] += p

    def isEmpty(self):
        return self.len == 0

    def deQueue(self):
        if self.isEmpty():
            return None
        q = self.queue
        Sorted = sorted(q.items(), key=lambda q:q[1], reverse=True) # 按值降序得元组列表
        self.queue[Sorted[0][0]] = 0
        self.len -= 1
        return Sorted[0][0]

    def reset(self):
        self.queue.clear()
        self.len = 0