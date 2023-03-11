import random
import numpy as np
from settings import listHerd, idHerds, listPride, idPrides, sizeCell, yearLength
from movement import relativeMovement
from position import relativePosition


class Group:
    def __init__(self, idGroup, memberList, x, y, bornFromSeparation=True):
        self.x = x
        self.y = y
        self.memberList = memberList
        self.id = idGroup
        self.bornFromSeparation = bornFromSeparation

    def movedType(self, yMov, xMov): pass
    def deadGroup(self): pass
    def notMovingGroup(self, stayingMembers, cells): pass

    def move(self, yMov, xMov, cells):
        stayingMembers = []
        numeroRandom = 0.2*random.random()
        for member in self.memberList:
            if member.energy/(member.lifetime*yearLength) > numeroRandom:
                member.energy -= 1
                if member.energy == 0:
                    self.memberList.remove(member)
                    if (len(self.memberList) == 0):
                        self.deadGroup(cells)
            else:
                stayingMembers.append(member)
        if len(stayingMembers) > 0:
            self.notMovingGroup(stayingMembers, cells)
        if (len(self.memberList) > 0):
            self.movedType(yMov, xMov, cells)
            self.x += xMov
            self.y += yMov

    def agingGroup(self, livingSpecies, cells):
        for member in self.memberList:
            member.aging(self.id, livingSpecies, cells)
        for member in self.memberList:
            if member.energy <= 0:
                self.memberList.remove(member)
                if (len(self.memberList) == 0):
                    self.deadGroup(cells)


class Herd(Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.lastVisitedCell = [0, 0]
        cells = kwargs.pop('cells', None)
        cells[self.y][self.x]['Herds'].append(self.id)

    def deadGroup(self, cells):
        listHerd[self.id] = None
        cells[self.y][self.x]['Herds'].remove(self.id)
        idHerds.remove(self.id)

    def notMovingGroup(self, stayingMembers, cells):
        idHerd = max(len(listHerd), 0)
        idHerds.append(idHerd)
        listHerd.append(Herd(idHerd, stayingMembers,
                        self.x, self.y, True, cells=cells))
        for member in stayingMembers:
            self.memberList.remove(member)
        if (len(self.memberList) == 0):
            self.deadGroup(cells)

    def movedType(self, yMov, xMov, cells):
        cells[self.y][self.x]['Herds'].remove(self.id)
        cells[self.y+yMov][self.x+xMov]['Herds'].append(self.id)

    def groupInteractions(self, cells):
        for member in self.memberList:
            threshold = np.random.normal(35, 5)
            if member.socialAttitude < threshold:
                idHerd = max(len(listHerd), 0)
                idHerds.append(idHerd)
                listHerd.append(
                    Herd(idHerd, [member], self.x, self.y, False, cells=cells))
                self.memberList.remove(member)
                if (len(self.memberList) == 0):
                    self.deadGroup(cells)

    def feed(self, preyEnergy):
        while True:
            for member in self.memberList:
                if (member.energy < 100):
                    member.energy += 1
                    preyEnergy -= 1
                    if preyEnergy <= 0:
                        break
                if (self.memberList[-1].energy == 100):
                    break
            else:
                continue
            break

    def decideStrategy(self, cells):
        if self.bornFromSeparation:
            self.bornFromSeparation = False
            return
        sight = self.memberList[0].sight
        subset = cells[self.y-sight:self.y +
                       sight+1, self.x-sight: self.x+sight+1]
        xMov = yMov = 0
        for y in range(sight+2):
            for x in range(sight+2):
                if subset[y][x]['type'] == 'ground':
                    if subset[y][x]['Prides'] != []:
                        xMov = x-1
                        yMov = y-1
                        break
            else:
                continue
            break
        else:
            if len(self.memberList) > 1:
                self.groupInteractions(cells)
            xRelative = relativePosition(self.x)
            yRelative = relativePosition(self.y)
            xMov = relativeMovement(xRelative)
            yMov = relativeMovement(yRelative)
            subset = list(cells[self.y-1: self.y+2, self.x-1: self.x+2].flat)
            subset.pop(4)
            subset = [cell for cell in subset if cell.get('type') == 'ground']
            while (True):
                # non si considera movimento stare fermo
                if (cells[self.y+yMov][self.x+xMov]['type'] == 'ground' and abs(xMov)+abs(yMov) != 0):
                    if len(subset) == 1:
                        break  # se c'è solo una cella a disposizione, anche se è stata visitata prima si andrà comunque lì
                    if (self.x+xMov != self.lastVisitedCell[1] or self.y+yMov != self.lastVisitedCell[0]):
                        break
                xMov = relativeMovement(xRelative)
                yMov = relativeMovement(yRelative)

        self.lastVisitedCell = [self.y, self.x]
        self.move(yMov, xMov, cells)


class Pride(Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        cells = kwargs.pop('cells', None)
        cells[self.y][self.x]['Prides'].append(self.id)

    def deadGroup(self, cells):
        listPride[self.id] = None
        cells[self.y][self.x]['Prides'].remove(self.id)
        idPrides.remove(self.id)

    def groupInteractions(self, possibleNewCells, cells):
        for member in self.memberList:
            threshold = np.random.normal(35, 5)
            if member.socialAttitude < threshold:
                idPride = max(len(listPride), 0)
                idPrides.append(idPride)
                newCell = random.choice(possibleNewCells)
                listPride.append(Pride(
                    idPride, [member], (self.x+newCell[1]), (self.y+newCell[0]), False, cells=cells))
                self.memberList.remove(member)

    def decideStrategy(self, cells):
        if self.bornFromSeparation:
            self.bornFromSeparation = False
            return
        shouldMove = False
        enemyNearby = False
        sight = self.memberList[0].sight
        subset = cells[self.y-sight: self.y +
                       sight+1, self.x-sight: self.x+sight+1]
        maxDensity = originalDensity = subset[sight][sight].get(
            'grass').density
        densityHerd = 0
        xMov = yMov = 0
        possibleNewCells = []  # if a new pride is created
        for y in range(sight+2):
            for x in range(sight+2):
                if subset[y][x]['type'] == 'ground':
                    density = subset[y][x].get('grass').density
                    possibleNewCells.append([y-1, x-1])
                    if subset[y][x]['Herds'] != [] and self.id not in subset[y][x]['Prides']:
                        enemyNearby = True
                        possibleNewCells = []
                        # aggiungi la possibilità che quando deve scappare dal predatore, se più celle sono safe allora il gruppo si può dividere
                        for row, col in np.ndindex((sight+2, sight+2)):
                            if ((row-y)**2+(col-x)**2 > 2) and subset[row][col]['type'] == 'ground':
                                if subset[row][col].get('grass').density > densityHerd:
                                    xMov = col-1
                                    yMov = row-1
                                    densityHerd = subset[row][col].get(
                                        'grass').density
                                possibleNewCells.append([row-1, col-1])
                        break

                    threshold = 80 if enemyNearby else sizeCell
                    if density/100*threshold > originalDensity and density > maxDensity:
                        maxDensity = density
                        xMov = x-1
                        yMov = y-1
            else:
                continue
            break
        if (xMov != 0 or yMov != 0):
            shouldMove = True
        if len(self.memberList) > 1 and len(possibleNewCells) > 0:
            self.groupInteractions(possibleNewCells, cells)
        if (not shouldMove):
            self.graze(cells)
        else:
            self.move(yMov, xMov, cells)

    def graze(self, cells):
        self.memberList.sort(key=lambda x: x.energy)
        while True:
            for member in self.memberList:
                if (member.energy < 100):
                    member.grazing()
                    cells[self.y][self.x].get('grass').density -= 1
                    if cells[self.y][self.x].get('grass').density == 0:
                        break
                if (self.memberList[0].energy == 100):
                    break
            else:
                continue
            break

    def movedType(self, yMov, xMov, cells):
        cells[self.y][self.x]['Prides'].remove(self.id)
        cells[self.y+yMov][self.x+xMov]['Prides'].append(self.id)
