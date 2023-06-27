import random
import numpy as np
from settings import sizeCell, yearLength
from movement import relativeMovement
from position import relativePosition


class Group:
    def __init__(self, y,x,memberList, bornFromSeparation=True):
        self.y = y
        self.x = x
        self.memberList = memberList
        self.bornFromSeparation = bornFromSeparation
        self.tracking = False
        self.visited = False

    def movedType(self, yMov, xMov): pass
    def deadGroup(self, cells, listGroup, idGroups): pass
    '''def notMovingGroup(self, stayingMembers, cells, listGroup, idGroups):
        idHerd = max(len(listGroup), 0)
        idGroups.append(idHerd)
        listGroup.append(Herd(idHerd, stayingMembers,
                              self.x, self.y, True, cells=cells))
        for member in stayingMembers:
            self.memberList.remove(member)
        if (len(self.memberList) == 0):
            self.deadGroup(cells, listGroup, idGroups)
    '''

    def move(self, yMov, xMov, cells):
        #stayingMembers = []
        numeroRandom = random.random()*0.7
        for member in self.memberList:
            if member.energy/100 < numeroRandom:
                member.energy -= 1
                if member.energy == 0:
                    self.memberList.remove(member)
                    if (len(self.memberList) == 0):
                        self.deadGroup(cells)
            '''else:
                #stayingMembers.append(member)
        if len(stayingMembers) > 0:
            print(stayingMembers, listGroup)
            self.notMovingGroup(stayingMembers, cells, listGroup, idGroups)'''
        if (len(self.memberList) > 0):
            self.movedType(yMov, xMov, cells)
            self.x += xMov
            self.y += yMov

    def agingGroup(self, livingSpecies, cells):
        populationChange = 0
        for member in self.memberList:
            populationChange+=member.aging(self.memberList, livingSpecies, cells, self.y, self.x)
        for member in self.memberList:
            if member.energy <= 0:
                self.memberList.remove(member)
                populationChange-=1
                if (len(self.memberList) == 0):
                    self.deadGroup(cells)
        return populationChange

class Herd(Group):
    def __init__(self, *args):
        super().__init__(*args)
        self.lastVisitedCell = [0, 0]

    def deadGroup(self, cells):
        cells[self.y][self.x]['Herds'].remove(self)

    def movedType(self, yMov, xMov, cells):
        cells[self.y][self.x]['Herds'].remove(self)
        cells[self.y+yMov][self.x+xMov]['Herds'].append(self)
    def groupInteractions(self, cells):
        for member in self.memberList:
            threshold = np.random.normal(35, 5)
            if member.socialAttitude < threshold:
                cells[self.y][self.x]['Herds'].append(Herd(self.y, self.x,[member], False))
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

    def decideStrategy(self, cells, y,x):
        self.visited = True
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
    def __init__(self, *args):
        super().__init__(*args)

    def deadGroup(self, cells):
        cells[self.y][self.x]['Prides'].remove(self)

    def groupInteractions(self, possibleNewCells, cells):
        for member in self.memberList:
            threshold = np.random.normal(35, 5)
            if member.socialAttitude < threshold:
                newCell = random.choice(possibleNewCells)
                cells[self.y+newCell[0], self.x+newCell[1]]['Prides'].append(Pride(
                    self.y+newCell[0], self.x+newCell[1],[member],  False))
                self.memberList.remove(member)

    def decideStrategy(self, cells, modifiedCells, y,x):
        self.visited = True
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
                    if subset[y][x]['Herds'] != [] and self not in subset[y][x]['Prides']:
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

                    threshold = 70 if enemyNearby else sizeCell
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
            self.groupInteractions(possibleNewCells, modifiedCells)
        if (not shouldMove):
            self.graze(modifiedCells)
        else:
            self.move(yMov, xMov, modifiedCells)

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
        cells[self.y][self.x]['Prides'].remove(self)
        cells[self.y+yMov][self.x+xMov]['Prides'].append(self)
