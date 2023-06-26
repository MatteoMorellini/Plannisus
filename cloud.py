import random
from settings import numCells
class Cloud():
    def __init__(self, yCell, xCell):
        self.dimensionX = random.randint(1, 3)
        self.dimensionY = random.randint(1, 3)
        self.direction = (random.randint(-3,3),random.randint(-3,3))
        while abs(self.direction[0])+abs(self.direction[0]) == 0:
            self.direction = (random.randint(-3,3),random.randint(-3,3))
        self.coords = set()
        for row in range(-self.dimensionY, self.dimensionY+1):
            for col in range(-self.dimensionX, self.dimensionX+1):
                if row == -self.dimensionY and yCell+row-1>=0 and xCell+col<numCells and xCell+col>=0:
                    if random.random()>.5: self.coords.add((yCell+row-1, xCell+col))
                elif row == self.dimensionY and yCell+row+1<numCells and xCell+col<numCells and xCell+col>=0:
                    if random.random()>.5: self.coords.add((yCell+row+1, xCell+col))
                elif col == self.dimensionX and xCell+col+1<numCells and yCell+row<numCells and yCell+row>=0:
                    if random.random()>.5: self.coords.add((yCell+row, xCell+col+1))
                elif col == -self.dimensionX and xCell+col-1>=0 and yCell+row<numCells and yCell+row>=0:
                    if random.random()>.5: self.coords.add((yCell+row, xCell+col-1))
                if yCell+row>= 0 and yCell+row<numCells and xCell+col >= 0 and xCell+col < numCells:
                    self.coords.add((yCell+row, xCell+col))
    def move(self):
        newPositions = set()
        for coord in self.coords:
            newPosition = (coord[0]+self.direction[0], coord[1]+self.direction[1])
            if newPosition[0] >= 0 and newPosition[1] >= 0 and newPosition[0]<numCells and newPosition[1]<numCells:
                newPositions.add(newPosition)
        self.coords = newPositions
        