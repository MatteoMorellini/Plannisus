import random 
import numpy as np
from vegetob import Vegetob
def createGrid(numCells):
  grid = np.array([[{'type': 'water'} for x in range(numCells)] for y in range(numCells)])
  for i in range(1, numCells-1):
    for j in range(1, numCells-1):
      if(random.random()>=.3):
        grid[i][j] = {"type": 'ground', 'grass': Vegetob(random.randint(0,50)), 'Herds': [], 'Prides': []}
  return grid