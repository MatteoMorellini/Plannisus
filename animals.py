import random
import numpy as np
from groups import Herd, Pride
from settings import yearLength


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
        energy = int(np.random.normal(self.energy, 10))
        while energy <= 0 or energy > 100:
            energy = int(np.random.normal(self.energy, 10))
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
        # si potrebbe pensare di fare questo in base alla popolazione nei 9 quadrati con centro
        # quello del pride che stiamo esaminando, se la densità è troppo alta allora meno figli
        if livingSpecies > 100:
            successors = 1
        elif livingSpecies > 20:
            successors = round(2*(1-sizePride))
        else:
            successors = 2
        for successor in range(0, successors):
            socialAttitude, energy, lifetime = self.generateOffspringProperties()
            Erbast(listPride[idPride].x, listPride[idPride].y,
                   energy, lifetime, socialAttitude, cells, listPride, idPrides, idPride)


class Carviz(Animal):
    def __init__(self, x, y, energy, lifetime, socialAttitude, cells, listHerd, idHerds, idHerd=None, sight=1):
        super().__init__(energy, lifetime, socialAttitude, sight)
        self.id = int(random.random()*1000)
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
        if livingSpecies > 100:
            successors = 1
        elif livingSpecies > 20:
            successors = round(2*(1-sizeHerd))
        else:
            successors = 2
        for successor in range(0, successors):
            socialAttitude, energy, lifetime = self.generateOffspringProperties()
            Carviz(listHerd[idHerd].x, listHerd[idHerd].y,
                   energy, lifetime, socialAttitude, cells, listHerd, idHerds, idHerd)
