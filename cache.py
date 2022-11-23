from collections import deque
import interface as I
class Cache(object):
    def __init__(self, LIMIT):
        self.cache = deque(maxlen=LIMIT)
    
    def has(self, element):
        return bool(element in self.cache)

    def hasKey(self, key):
        for x in self.cache:
            if key == x[0]:
                return True
        return False
    
    def getByKey(self, key):
        for x in self.cache:
            if key == x[0]:
                return x
        return "Error"

    def removeByKey(self, elementKey):
        if self.hasKey(elementKey):
            self.cache.remove(self.getByKey(elementKey))
            return True
        return False
    
    def insert(self, elementKey, elementValue):
        print("Chegou no insert cache")
        obj = (elementKey, elementValue)
        self.removeByKey(elementKey)
        self.cache.append(obj)
        print("Saiu do insert cache")
    
    def update(self, elementKey, newValue):
        isRemoved = self.removeByKey(elementKey)
        if isRemoved == True:
            self.insert(elementKey, newValue)
            return True
        return False

    

    def print(self):
        print('Cache: [', end='')
        N = len(self.cache)
        for i in range(N):
            x = self.cache[i]
            if i < N-1:
                print(x, end=", ")
            else:
                print(x, end="]\n")

#Testing
# d = Cache(3)
# d.insert(I.newUserCID(I.takeHash("1")))
# d.insert(I.newUserCID(I.takeHash("2")))
# d.insert(I.newUserCID(I.takeHash("1")))
# d.insert(I.newUserCID(I.takeHash("1")))
# d.insert(I.newUserCID(I.takeHash("2")))
# d.insert(I.newUserCID(I.takeHash("1")))
# d.print()
