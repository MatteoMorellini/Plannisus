import random
import numpy as np
from groups import Herd, Pride
from settings import yearLength
import math


class Animal():
    def __init__(self, energy, lifetime, socialAttitude, sight=1):
        self._energy = energy
        self.lifetime = lifetime
        self.age = 0
        self.socialAttitude = socialAttitude
        self.sight = sight

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, new_energy):
        if new_energy < 100:
            self._energy = new_energy
        if new_energy >= 100:
            self._energy = 100

    def generateOffspringProperties(self):
        socialAttitude = np.random.normal(self.socialAttitude, 10)
        while (socialAttitude > 100 or socialAttitude < 0):
            socialAttitude = np.random.normal(self.socialAttitude, 10)
        energy = int(np.random.normal(self.energy-5, 10))
        while energy <= 0 or energy > 100:
            energy = int(np.random.normal(self.energy-5, 10))
        lifetime = random.randint(self.lifetime-1, self.lifetime+1)
        while lifetime < 1 or lifetime > 10:
            lifetime = random.randint(self.lifetime-1, self.lifetime+1)
        return socialAttitude, energy, lifetime


class Erbast(Animal):
    def __init__(self, y,x, energy, lifetime, socialAttitude, cells, sight=1):
        super().__init__(energy, lifetime, socialAttitude, sight)
        if cells[y,x]['Prides'] != []:
            cells[y,x]['Prides'][0].memberList.append(self)
        else:
            cells[y][x]['Prides'].append(Pride(y, x,[self]))
    def grazing(self):
        self.energy += 1

    def aging(self, memberList, livingSpecies, cells, y, x):
        self.age += 1
        if self.age % yearLength == 0:
            self.energy -= 1
        if self.age >= self.lifetime*yearLength:
            return self.generateOffspring(memberList, livingSpecies, cells, y ,x)
        return 0

    def generateOffspring(self, memberList, livingSpecies, cells, y,x):
        sizePride = len(memberList)/livingSpecies
        memberList.remove(self)
        subset = list(cells[y-1: y+2, x-1: x+2].flat)
        subset.pop(4)
        neighbors = sum(
            1 for cell in subset if 'Prides' in cell and cell['Prides'])
        successors = 1 if (
            neighbors/8 >= 0.2 or (livingSpecies > 20 and sizePride > 0.25)) else 2
        for _ in range(0, successors):
            socialAttitude, energy, lifetime = self.generateOffspringProperties()
            Erbast(y,x, energy, lifetime, socialAttitude, cells)
        return successors-1

class Carviz(Animal):
    def __init__(self, y,x, energy, lifetime, socialAttitude, cells, sight=1):
        super().__init__(energy, lifetime, socialAttitude, sight)
        if cells[y,x]['Herds'] != []:
            cells[y,x]['Herds'][0].memberList.append(self)
        else:
            cells[y][x]['Herds'].append(Herd(y,x,[self]))

    def aging(self, memberList, livingSpecies, cells, y ,x):
        self.age += 1
        if self.age % yearLength == 0:
            self.energy -= 1
        if self.age >= self.lifetime*yearLength:
            return self.generateOffspring(memberList, livingSpecies,cells, y, x)
        return 0

    def generateOffspring(self, memberList, livingSpecies, cells, y,x):
        sizeHerd = len(memberList)/livingSpecies
        memberList.remove(self)
        subset = list(cells[y-1: y+2,x-1:x+2].flat)
        subset.pop(4)
        neighbors = sum(
            1 for cell in subset if 'Herds' in cell and cell['Herds'])
        successors = 1 if (
            neighbors/8 >= 0.2 or (livingSpecies > 20 and sizeHerd >= 0.25)) else 2
        for _ in range(0, successors):
            socialAttitude, energy, lifetime = self.generateOffspringProperties()
            Carviz(y,x, energy, lifetime, socialAttitude, cells)
        return successors-1