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
    def __init__(self, x, y, energy, lifetime, socialAttitude, cells, listPride, idPrides, idPride=None, sight=1):
        super().__init__(energy, lifetime, socialAttitude, sight)
        if idPride in idPrides:
            listPride[idPride].memberList.append(self)
        else:
            idPride = idPrides[-1]+1 if len(idPrides) > 0 else 0
            idPrides.append(idPride)
            listPride.append(Pride(idPride, [self], x, y, cells=cells))

    def grazing(self):
        self.energy += 1

    def aging(self, idPride, livingSpecies, cells, listPride, idPrides):
        self.age += 1
        if self.age % yearLength == 0:
            self.energy -= 1
        if self.age >= self.lifetime*yearLength:
            self.generateOffspring(
                idPride, livingSpecies, cells, listPride, idPrides)

    def generateOffspring(self, idPride, livingSpecies, cells, listPride, idPrides):
        sizePride = len(listPride[idPride].memberList)/livingSpecies
        listPride[idPride].memberList.remove(self)
        subset = list(cells[listPride[idPride].y-1: listPride[idPride].y+2,
                      listPride[idPride].x-1: listPride[idPride].x+2].flat)
        subset.pop(4)
        neighbors = sum(
            1 for cell in subset if 'Prides' in cell and cell['Prides'])
        successors = 1 if (
            neighbors/8 >= 0.2 or (livingSpecies > 20 and sizePride > 0.25)) else 2
        for _ in range(0, successors):
            socialAttitude, energy, lifetime = self.generateOffspringProperties()
            Erbast(listPride[idPride].x, listPride[idPride].y,
                   energy, lifetime, socialAttitude, cells, listPride, idPrides, idPride)


class Carviz(Animal):
    def __init__(self, x, y, energy, lifetime, socialAttitude, cells, listHerd, idHerds, idHerd=None, sight=1):
        super().__init__(energy, lifetime, socialAttitude, sight)
        if idHerd in idHerds:
            listHerd[idHerd].memberList.append(self)
        else:
            idHerd = idHerds[-1]+1 if len(idHerds) > 0 else 0
            idHerds.append(idHerd)
            listHerd.append(Herd(idHerd, [self], x, y, cells=cells))

    def aging(self, idHerd, livingSpecies, cells, listHerd, idHerds):
        self.age += 1
        if self.age % yearLength == 0:
            self.energy -= 1
        if self.age >= self.lifetime*yearLength:
            self.generateOffspring(idHerd, livingSpecies,
                                   cells, listHerd, idHerds)

    def generateOffspring(self, idHerd, livingSpecies, cells, listHerd, idHerds):
        sizeHerd = len(listHerd[idHerd].memberList)/livingSpecies
        listHerd[idHerd].memberList.remove(self)
        subset = list(cells[listHerd[idHerd].y-1: listHerd[idHerd].y+2,
                      listHerd[idHerd].x-1: listHerd[idHerd].x+2].flat)
        subset.pop(4)
        neighbors = sum(
            1 for cell in subset if 'Herds' in cell and cell['Herds'])
        successors = 1 if (
            neighbors/8 >= 0.2 or (livingSpecies > 20 and sizeHerd >= 0.25)) else 2

        for _ in range(0, successors):
            socialAttitude, energy, lifetime = self.generateOffspringProperties()
            Carviz(listHerd[idHerd].x, listHerd[idHerd].y,
                   energy, lifetime, socialAttitude, cells, listHerd, idHerds, idHerd)
