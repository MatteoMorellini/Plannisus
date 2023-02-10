import random
import numpy as np
import pygame
import time
import os
import math

listHerd = [] #listHerd=[istance1, istance2 etc...]
idHerds = []
listPride = []
idPrides = []

parameters = {'sizeCell': [20, 10, 60], 'yearLength': [10,20,30]}
dimensions = (600,600)
sizeCell = 20
numCells = int(dimensions[0]/sizeCell)
rgbConfiguration = True if sizeCell < 20 else False

yearLength = 10

COLOR_WATER = (0,127,255)
COLOR_GRID = (40,40,40)
COLOR_GROUND = (150,75,0)
COLOR_VEGETOB = (0,154,23)
COLOR_HERD = (200,0,0)
COLOR_PRIDE = (231,185,40)

class Vegetob():
  def __init__(self, density):
    self._density = density
  def grow(self):
    self.density+=0.2
  @property
  def density(self):
    return self._density
  @density.setter
  def density(self, new_density):
    if new_density >= 0 and new_density <= 100:
      self._density = new_density
    elif new_density>100:
      self._density = 100
    else: self._density = 0


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
    if new_energy>=100:
      self._energy = 100
  
  def generateOffspringProperties(self):
    socialAttitude = np.random.normal(self.socialAttitude, 10)
    while (socialAttitude>100 or socialAttitude<0):
      socialAttitude = np.random.normal(self.socialAttitude, 10)
    energy = np.random.normal(60, 10)
    while energy<0 or energy>100:
      energy = np.random.normal(60,10)
    lifetime = random.randint(self.lifetime-1, self.lifetime+1)
    while lifetime<1 or lifetime>10:
      lifetime = random.randint(self.lifetime-1, self.lifetime+1)
    return socialAttitude, energy, lifetime

class Erbast(Animal):
  def __init__(self, x, y, energy, lifetime, socialAttitude, idPride=None, sight=1):
    super().__init__(energy, lifetime, socialAttitude, sight)
    if idPride in idPrides:
      listPride[idPride].memberList.append(self)
    else:
      idPride = idPrides[-1]+1 if len(idPrides)>0 else 0
      idPrides.append(idPride)
      listPride.append(Pride(idPride, [self], x, y))
  def grazing(self):
    self.energy+=1
  
  def aging(self, idPride, livingSpecies):
    self.age += 1
    if self.age % yearLength == 0: self.energy -= 1
    if self.age >= self.lifetime*yearLength:
      self.generateOffspring(idPride, livingSpecies)
    
  def generateOffspring(self, idPride, livingSpecies):
    sizePride = len(listPride[idPride].memberList)/livingSpecies
    listPride[idPride].memberList.remove(self)
    #si potrebbe pensare di fare questo in base alla popolazione nei 9 quadrati con centro
    #quello del pride che stiamo esaminando, se la densità è troppo alta allora meno figli
    if livingSpecies > 200:
      successors = 1
    elif livingSpecies > 50:
      successors = round(2*(1-sizePride))
    else: successors = 2
    for successor in range(0,successors):
      energy, socialAttitude, lifetime = self.generateOffspringProperties()
      Erbast(listPride[idPride].x, listPride[idPride].y, energy, lifetime, socialAttitude, idPride)


class Carviz(Animal):
  def __init__(self, x, y, energy, lifetime, socialAttitude, idHerd=None, sight=1):
    super().__init__(energy, lifetime, socialAttitude, sight)
    if idHerd in idHerds: 
      listHerd[idHerd].memberList.append(self)
    else:
      idHerd = idHerds[-1]+1 if len(idHerds)>0 else 0
      idHerds.append(idHerd)
      listHerd.append(Herd(idHerd, [self], x, y))
  def aging(self, idHerd, livingSpecies):
    self.age += 1
    if self.age % yearLength == 0: self.energy -= 1
    if self.age >= self.lifetime*yearLength:
      self.generateOffspring(idHerd, livingSpecies)
  def generateOffspring(self, idHerd, livingSpecies):
    sizeHerd = len(listHerd[idHerd].memberList)/livingSpecies
    listHerd[idHerd].memberList.remove(self)
    if livingSpecies > 100:
      successors = 1
    elif livingSpecies > 20:
      successors = round(2*(1-sizeHerd))
    else: successors = 2

    for successor in range(0,successors):
      energy, socialAttitude, lifetime = self.generateOffspringProperties()
      Carviz(listHerd[idHerd].x, listHerd[idHerd].y, energy, lifetime, socialAttitude, idHerd)

def relativePosition(pos):
  relativePosition = pos / ((600/sizeCell)-2) #perchè se ci sono 10 celle, 2 sono i bordi quindi a noi interessano 8
  rel = 0.3 - (relativePosition * 0.3)
  return rel

def relativeMovement(rel):
  randomNumber = random.random()
  if(randomNumber <= 0.3):
    addPos = 0
  elif(randomNumber > 0.3 and randomNumber < 0.50+rel):
    addPos = 1
  else:
    addPos = -1
  return addPos

class Group():
  def __init__(self,idGroup,memberList, x, y):
    self.x = x
    self.y = y
    self.memberList = memberList
    self.id = idGroup
  def movedType(self, yMov, xMov):
    pass
  def deadGroup(self): pass
  def move(self, yMov, xMov):
    self.movedType(yMov, xMov)
    self.x += xMov
    self.y += yMov
    for member in self.memberList:
      member.energy -= 1    
      if member.energy<=0: 
        self.memberList.remove(member)
        if(len(self.memberList)==0):
          self.deadGroup()
  def agingGroup(self, livingSpecies):
    for member in self.memberList:
      member.aging(self.id, livingSpecies)

class Herd(Group):
  def __init__(self, *args):
    super().__init__(*args)
    self.lastVisitedCell = [0,0]
    cells[self.y][self.x]['Herds'].append(self.id)
  def deadGroup(self):
    listHerd[self.id] = None
    cells[self.y][self.x]['Herds'].remove(self.id)
    idHerds.remove(self.id)

  def movedType(self, yMov, xMov):
    cells[self.y][self.x]['Herds'].remove(self.id)
    cells[self.y+yMov][self.x+xMov]['Herds'].append(self.id)
  
  def groupInteractions(self):
    for member in self.memberList:
      threshold = np.random.normal(35,5)
      if member.socialAttitude < threshold:
        idHerd= max(len(listHerd), 0)
        idHerds.append(idHerd)
        listHerd.append(Herd(idHerd, [member], self.x, self.y))
        self.memberList.remove(member)

  def feed(self, preyEnergy):
    while True:
      for member in self.memberList:
        if(member.energy<100):
          member.energy+=1
          preyEnergy-=1
          if preyEnergy <= 0: break
        if(self.memberList[-1].energy==100):
          break
      else:continue
      break    

  def decideStrategy(self):
    sight = self.memberList[0].sight
    subset = cells[self.y-sight:self.y+sight+1, self.x-sight:self.x+sight+1]
    xMov = yMov = 0
    for y in range(sight+2):
      for x in range(sight+2):
        if subset[y][x]['type'] == 'ground':
          if subset[y][x]['Prides'] != []:
            xMov = x-1
            yMov = y-1
            break
      else:continue
      break
    else:
      if len(self.memberList)>1: self.groupInteractions()
      xRelative = relativePosition(self.x)
      yRelative = relativePosition(self.y)
      xMov = relativeMovement(xRelative)
      yMov = relativeMovement(yRelative)
      subset = list(cells[self.y-1:self.y+2, self.x-1:self.x+2].flat)
      subset.pop(4)
      subset = [cell for cell in subset if cell.get('type') == 'ground']
      while(True):
        if(cells[self.y+yMov][self.x+xMov]['type'] == 'ground' and abs(xMov)+abs(yMov)!=0): 
          if(len(subset)==1): break
          if(self.x+xMov != self.lastVisitedCell[1] or self.y+yMov != self.lastVisitedCell[0]): break
        xMov = relativeMovement(xRelative)
        yMov = relativeMovement(yRelative)
    self.lastVisitedCell = [self.y, self.x]
    self.move(yMov, xMov)
    
class Pride(Group):
  def __init__(self, *args):
    super().__init__(*args)
    cells[self.y][self.x]['Prides'].append(self.id)
    self.bornFromSeparation = False

  def deadGroup(self):
    listPride[self.id] = None
    cells[self.y][self.x]['Prides'].remove(self.id)
    idPrides.remove(self.id)

  def groupInteractions(self, possibleNewCells):
    for member in self.memberList:
      threshold = np.random.normal(35,5)
      if member.socialAttitude < threshold:
        idPride= max(len(listPride), 0)
        idPrides.append(idPride)
        newCell = random.choice(possibleNewCells)
        listPride.append(Pride(idPride, [member], (self.x+newCell[1]), (self.y+newCell[0])))
        self.memberList.remove(member)
        listPride[-1].bornFromSeparation = True
        

  def decideStrategy(self):
    if self.bornFromSeparation: 
      self.bornFromSeparation=False
      return
    shouldMove = False
    enemyNearby = False
    sight = self.memberList[0].sight
    subset = cells[self.y-sight:self.y+sight+1, self.x-sight:self.x+sight+1]
    maxDensity = originalDensity = subset[sight][sight].get('grass').density
    densityHerd = 0
    xMov = yMov = 0
    possibleNewCells = [] #if a new pride is created
    for y in range(sight+2):
      for x in range(sight+2):
        if subset[y][x]['type'] == 'ground':
          density = subset[y][x].get('grass').density
          possibleNewCells.append([y-1, x-1])
          if subset[y][x]['Herds'] != [] and self.id not in subset[y][x]['Prides']:
            enemyNearby = True
            possibleNewCells = []
            #aggiungi la possibilità che quando deve scappare dal predatore, se più celle sono safe allora il gruppo si può dividere
            for row, col in np.ndindex((sight+2, sight+2)):
              if((row-y)**2+(col-x)**2>2) and subset[row][col]['type']=='ground': 
                if subset[row][col].get('grass').density > densityHerd: 
                  xMov = col-1
                  yMov = row-1
                  densityHerd = subset[row][col].get('grass').density
                possibleNewCells.append([row-1, col-1])
            break
          
          threshold = 80 if enemyNearby else sizeCell
          if density/100*threshold > originalDensity and density > maxDensity:
            maxDensity = density
            xMov = x-1
            yMov = y-1    
      else:continue
      break
    if(xMov != 0 or yMov != 0): shouldMove = True
    if len(self.memberList)>1 and len(possibleNewCells)>0: self.groupInteractions(possibleNewCells)
    if(not shouldMove):
      self.graze()
    else:
      self.move(yMov, xMov)
  def graze(self):
    self.memberList.sort(key=lambda x: x.energy)
    while True:
      for member in self.memberList:
        if(member.energy<100):
            member.grazing()
            cells[self.y][self.x].get('grass').density-=1
            if cells[self.y][self.x].get('grass').density == 0: break
        if(self.memberList[0].energy==100):
          break
      else:continue
      break
  def movedType(self, yMov, xMov):
    cells[self.y][self.x]['Prides'].remove(self.id)
    cells[self.y+yMov][self.x+xMov]['Prides'].append(self.id)

def hunt():
  for row, col in np.ndindex(cells.shape):
    if cells[row][col]['type']=='ground':
      if(cells[row][col]['Herds']!=[] and cells[row][col]['Prides'] != []):
        idHerd = cells[row][col]['Herds'][0]
        idPride = cells[row][col]['Prides'][0]
        stdHerd = np.std([member.socialAttitude for member in listHerd[idHerd].memberList])
        stdPride = np.std([member.socialAttitude for member in listPride[idPride].memberList])
        listHerd[idHerd].memberList.sort(key =lambda member: member.energy, reverse = True)
        lenHerd = len(listHerd[idHerd].memberList)
        listPride[idPride].memberList.sort(key =lambda member: member.energy, reverse = True)
        lenPride = len(listPride[idPride].memberList)
        #utilizzando la funzione list creo una nuova istanza della lista che non fa riferimento alla stessa cella di memoria
        #perchè non vogliamo che la social attitude si sommi poi durante lo svolgimento normale
        newEnergyPredator = [member.energy for member in listHerd[idHerd].memberList]
        newEnergyPrey = [member.energy for member in listPride[idPride].memberList]
        if lenHerd>lenPride:
          for i in range(lenHerd-lenPride): 
            predatorToJoin = random.randint(0,lenPride)
            newEnergyPredator[i] = (listHerd[idHerd].memberList[predatorToJoin].energy + listHerd[idHerd].memberList[lenPride+i].energy)
          numberOfFights = lenPride
        elif lenPride > lenHerd:
          for i in range(lenPride-lenHerd):
            preyToJoin = random.randint(0,lenHerd)
            newEnergyPrey[i] = (listPride[idPride].memberList[preyToJoin].energy + listPride[idPride].memberList[lenHerd+i].energy)
          numberOfFights = lenHerd
        else:
          numberOfFights = lenPride
        for i in range(numberOfFights):
          if newEnergyPredator[i]-stdHerd > newEnergyPrey[i]-stdPride:
            listHerd[idHerd].feed(newEnergyPrey[i])
          else:
            listHerd[idHerd].feed(newEnergyPrey[i]-(stdPride-20))
        listPride[idPride] = None
        idPrides.remove(idPride)
        cells[row][col]['Prides'].remove(idPride)
          
          #due casi: i predatori sono più delle prede o le prede sono più dei predatori
          #nel primo caso ordino in ordine decrescente per energia e sommo
        
def createGrid(numCells):
  grid = np.array([[{'type': 'water'} for x in range(numCells)] for y in range(numCells)])
  for i in range(1, numCells-1):
    for j in range(1, numCells-1):
      if(random.random()>=.3):
        grid[i][j] = {"type": 'ground', 'grass': Vegetob(random.randint(0,50)), 'Herds': [], 'Prides': []}
  return grid
def checkConnections(numCells, grid):
  for i in range(1,numCells-1):
      for j in range(1,numCells-1):
        subset = grid[i-1:i+2, j-1:j+2]
        if(grid[i][j].get('type')=='ground' and len([1 for cell in subset.flat if cell.get('type') == 'ground']) == 1):
          xRnd = random.randint(-1,1)
          yRnd = random.randint(-1,1)
          while((abs(xRnd) + abs(yRnd)) !=1 or (i+yRnd == 0 or i+yRnd == 9) or (j+xRnd == 0 or j+xRnd ==9)):
            xRnd = random.randint(-1,1)
            yRnd = random.randint(-1,1)
          grid[i+yRnd][j+xRnd]['type'] = 'ground'
  return grid

def vegetobKiller(row, col):
  subset = list(cells[row-1:row+2, col-1:col+2].flat)
  subset.pop(4)
  subset = [cell for cell in subset if cell.get('type') == 'ground']
  nearFullGrowth = len([cell.get('grass').density for cell in subset if cell.get('grass').density==100])
  if nearFullGrowth == len(subset)-1 and nearFullGrowth > 1:
    for idPride in cells[row][col]['Prides']:
      listPride[idPride] = None
      idPrides.remove(idPride)
    cells[row][col]['Prides'] = []
  elif nearFullGrowth == len(subset): 
    #ho rimesso i Pride perchè o girano in una cella con energia al massimo oppure considero l'ipotesi in 
    #cui un gruppo nasca su un'isola dove senza questo controllo vivrebbe per sempre
    for idHerd in cells[row][col]['Herds']:
      listHerd[idHerd] = None
      idHerds.remove(idHerd)
    cells[row][col]['Herds'] = []
    for idPride in cells[row][col]['Prides']:
      listPride[idPride] = None
      idPrides.remove(idPride)
    cells[row][col]['Prides'] = []

def joinPrides():
  for row, col in np.ndindex(cells.shape):
    if cells[row][col]['type']=='ground':
      if len(cells[row][col]['Prides']) > 1:
        cells[row][col]['Prides'].sort(key =lambda idGroup: len(listPride[idGroup].memberList), reverse = True)
        for idGroup in cells[row][col]['Prides'][1:]:
          listPride[cells[row][col]['Prides'][0]].memberList += listPride[idGroup].memberList
          listPride[idGroup] = None
          cells[row][col]['Prides'].remove(idGroup)
          idPrides.remove(idGroup)

def handleHerds():
  for row, col in np.ndindex(cells.shape):
    if cells[row][col]['type']=='ground':
      numHerds = len(cells[row][col]['Herds'])
      if numHerds > 1:
        cells[row][col]['Herds'].sort(key =lambda idGroup: len(listHerd[idGroup].memberList), reverse = True)
        avgSAHerds = np.average([np.average([carviz.socialAttitude for carviz in listHerd[cells[row][col]['Herds'][index]].memberList]) for index in range(len(cells[row][col]['Herds']))])
        threshold = np.random.normal(60, 10)
        if(avgSAHerds < threshold):
          #se ci sono più di 2 Herds nella stessa casella e abbiamo calcolato che combatteranno allora mettiamo da parte i due 
          # gruppi più numeri e gli altri li trattiamo nel seguente modo: 
          #se la std è bassa si uniranno tutti i componenti allo stesso gruppo scelto a caso tra i due, altrimenti saranno coinvolti nello scontro rimanendo nella stessa orda
          if numHerds>2: 
            minorHerdsId = cells[row][col]['Herds'][2:]
            for minorHerdId in minorHerdsId:
              stdHerdSA = np.std([member.socialAttitude for member in listHerd[minorHerdId].memberList])
              if(stdHerdSA<20): 
                majorGroupToJoin = random.randint(0,1)
                listHerd[cells[row][col]['Herds'][majorGroupToJoin]].memberList += listHerd[minorHerdId].memberList
                listHerd[minorHerdId] = None
                idHerds.remove(minorHerdId)
                cells[row][col]['Herds'].remove(minorHerdId)
                numHerds-=1
          while numHerds > 1:
            fightingHerd1 = listHerd[cells[row][col]['Herds'][0]]
            if len(fightingHerd1.memberList)>1: fightingHerd1.memberList.sort(key =lambda member: member.energy, reverse = True)
            fightingHerd2 = listHerd[cells[row][col]['Herds'][1]]
            if len(fightingHerd2.memberList)>1: fightingHerd2.memberList.sort(key =lambda member: member.energy, reverse = True)
            while True:
              if(fightingHerd1.memberList[0].energy-fightingHerd2.memberList[0].energy>0):
                fightingHerd1.memberList[0].energy -= fightingHerd2.memberList[0].energy
                fightingHerd2.memberList.pop(0)
                if(fightingHerd2.memberList==[]):
                  numHerds-=1
                  listHerd[cells[row][col]['Herds'][1]] = None
                  idHerds.remove(cells[row][col]['Herds'][1])
                  cells[row][col]['Herds'].pop(1)
                  break
              else:
                fightingHerd2.memberList[0].energy -= fightingHerd1.memberList[0].energy
                fightingHerd1.memberList.pop(0)
                if(fightingHerd1.memberList==[]):
                  numHerds-=1
                  listHerd[cells[row][col]['Herds'][0]] = None
                  idHerds.remove(cells[row][col]['Herds'][0])
                  cells[row][col]['Herds'].pop(0)
                  break
        else:
          for idGroup in cells[row][col]['Herds'][1:]:
            listHerd[cells[row][col]['Herds'][0]].memberList += listHerd[idGroup].memberList
            listHerd[idGroup] = None
            idHerds.remove(idGroup)
            cells[row][col]['Herds'].remove(idGroup) 

def livingSpecies(socialGroups):
  sum = 0
  for group in socialGroups:
    sum = sum + len(group.memberList) if group is not None else sum + 0
  return sum

def attributeNewAnimal(sort):
  idGroup = None
  xCreature = random.randint(1,numCells-1)
  yCreature = random.randint(1,numCells-1)
  while(cells[yCreature][xCreature]['type'] != 'ground'):
    xCreature = random.randint(1,numCells-1)
    yCreature = random.randint(1,numCells-1)
  if sort=='Erbast' and cells[yCreature][xCreature]['Prides']!=[]:
    idGroup = cells[yCreature][xCreature]['Prides'][0]
  elif sort=='Carviz' and cells[yCreature][xCreature]['Herds']!=[]:
    idGroup = cells[yCreature][xCreature]['Herds'][0]
  energyCreature = np.random.normal(60, 10)
  while energyCreature<0 or energyCreature>100:
    energyCreature = np.random.normal(60,10)
  lifetimeCreature = random.randint(2,6)
  socialAttitudeCreature = np.random.normal(50, 20)
  while socialAttitudeCreature<0 or socialAttitudeCreature>100:
    socialAttitudeCreature = np.random.normal(50, 20)
  return xCreature, yCreature, energyCreature, lifetimeCreature, socialAttitudeCreature, idGroup

def generateAnimals(nErbast, nCarviz):
  for i in range(nErbast):
    xCreature, yCreature, energyCreature, lifetimeCreature, socialAttitudeCreature, idPride = attributeNewAnimal('Erbast')
    Erbast(xCreature, yCreature, energyCreature, lifetimeCreature, socialAttitudeCreature, idPride)
  for k in range(nCarviz):
    xCreature, yCreature, energyCreature, lifetimeCreature, socialAttitudeCreature, idHerd = attributeNewAnimal('Carviz')
    Carviz(xCreature, yCreature, energyCreature, lifetimeCreature, socialAttitudeCreature, idHerd)

def update(screen, cells, size):
  if rgbConfiguration:
    for row, col in np.ndindex(cells.shape):
      if(cells[row, col].get('type') == 'water'):
        pygame.draw.rect(screen, (144,144,144), (col*size, row*size, size-1, size-1))
      else:
        redIntensity = greenIntensity = blueIntensity = 0
        
        herds = cells[row][col].get('Herds')
        prides = cells[row][col].get('Prides')
        if(len(herds)==0 and len(prides)==0):
          vegetob = cells[row][col].get('grass')
          greenIntensity = 255 if vegetob.density == 0 else 255-155*(vegetob.density/100)
        else:
          if len(prides) > 0:
            sizePride = 0
            for idPride in prides:
              sizePride += len(listPride[idPride].memberList)/livingSpecies(listPride)
            blueIntensity = 255 - round(155*sizePride)
          if len(herds)>0:
            sizeHerd = 0
            for idHerd in herds:
              sizeHerd += len(listHerd[idHerd].memberList)/livingSpecies(listHerd)
            redIntensity = 255 - round(155*sizeHerd)

        pygame.draw.rect(screen, (redIntensity, greenIntensity, blueIntensity), (col*size, row*size, size-1, size-1))

  else:
    for row, col in np.ndindex(cells.shape):
      color = COLOR_WATER if cells[row, col].get('type') == 'water' else COLOR_GROUND
      pygame.draw.rect(screen, color, (col*size, row*size, size-1, size-1))
      if color == COLOR_GROUND:
        vegetob = cells[row][col].get('grass')
        vegetobSize = 0 if vegetob.density == 0 else vegetob.density/100*(size-1)
        pygame.draw.rect(screen, COLOR_VEGETOB, (col*size, row*size, vegetobSize, vegetobSize))
        herds = cells[row][col].get('Herds')
        prides = cells[row][col].get('Prides')
        if len(prides) > 0:
          for idPride in prides:
            if(len(listPride[idPride].memberList)>0):
              sizePride = len(listPride[idPride].memberList)/livingSpecies(listPride)
              xRnd = random.randint(1,size-int((0.3*size*sizePride)+(size/5)+2))
              yRnd = random.randint(1,size-int((0.3*size*sizePride)+(size/5)+2))
              pygame.draw.rect(screen, (0,0,0), (col*size+xRnd-1, row*size+yRnd-1, (0.3*size*sizePride)+(size/5)+2, (0.3*size*sizePride)+(size/5)+2))
              pygame.draw.rect(screen, COLOR_PRIDE, (col*size+xRnd, row*size+yRnd, (0.3*size*sizePride)+(size/5), (0.3*size*sizePride)+(size/5)))
            #si moltiplica x0.3 perchè al massimo un branco può essere grande 1/2 della cella
        if len(herds) > 0:
          for idHerd in herds:
            if(len(listHerd[idHerd].memberList)>0):
              sizeHerd = len(listHerd[idHerd].memberList)/livingSpecies(listHerd)
              xRnd = random.randint(1,size-int((0.3*size*sizeHerd)+(size/5)+2))
              yRnd = random.randint(1,size-int((0.3*size*sizeHerd)+(size/5)+2))
              pygame.draw.rect(screen, (0,0,0), (col*size+xRnd-1, row*size+yRnd-1, (0.3*size*sizeHerd)+(size/5)+2, (0.3*size*sizeHerd)+(size/5)+2))
              pygame.draw.rect(screen, COLOR_HERD, (col*size+xRnd, row*size+yRnd, (0.3*size*sizeHerd)+(size/5), (0.3*size*sizeHerd)+(size/5)))

cells = createGrid(numCells)

def main():
  pygame.init()
  screen = pygame.display.set_mode(dimensions)
  screen.fill(COLOR_GRID)
  update(screen, cells, sizeCell)
  pygame.display.flip()
  pygame.display.update()
  gameStarted = False
  firstGeneration = True
  running = False
  generationCounter = 0
  pause = 0
  while True:
    if gameStarted and firstGeneration:
      generateAnimals(10,10)
      update(screen, cells, sizeCell)
      pygame.display.update()
      firstGeneration = False
      gameStarted = True
    if gameStarted and running:
      for row, col in np.ndindex(cells.shape):
        if cells[row][col]['type'] == 'ground':
          cells[row][col].get('grass').grow()
          vegetobKiller(row,col)

      for member in filter(lambda pride: pride is not None, listPride):
        member.decideStrategy()

      #se un Herd deve ancora muoversi e ha un Pride che costretto si è mosso nella sua cella, allora troverà xMov=yMov=0
      for member in filter(lambda herd: herd is not None, listHerd):
        member.decideStrategy()

      update(screen, cells, sizeCell)
      pygame.display.update()
      #time.sleep(pause)
      joinPrides()
      handleHerds()
      update(screen, cells, sizeCell)
      pygame.display.update()
      #time.sleep(pause)
      hunt()

      for member in filter(lambda pride: pride is not None, listPride):
        member.agingGroup(livingSpecies(listPride))
      for member in filter(lambda herd: herd is not None, listHerd):
        member.agingGroup(livingSpecies(listHerd))
      update(screen, cells, sizeCell)
      pygame.display.update()
      if (livingSpecies(listHerd) == 0):
        print(f'Match lasted {generationCounter} rounds')
        pygame.quit()
        return
      else: generationCounter += 1
      #running = not running
      #time.sleep(2*pause)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        return
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
          update(screen, cells, sizeCell)
          pygame.display.update()
          running = not running
      if event.type == pygame.KEYDOWN:
        if(event.key == 115): 
          os.system('cls' if os.name == 'nt' else 'clear')
          print('++++++++++++++++++++++')
          print('GAME STARTED')
          print('++++++++++++++++++++++')
          gameStarted = True
        elif(event.key == 43 and pause < 5):
          pause += 0.1
        elif(event.key == 45 and pause >=0.1):
          pause-=0.1
      if pygame.mouse.get_pressed()[0]:
        pos= pygame.mouse.get_pos()
        cell = cells[pos[1] // sizeCell] [pos[0] // sizeCell]
        print('Cell of type:', cell.get('type'), '\nCoordinates:', pos[1]//sizeCell, pos[0]//sizeCell)
        if cell.get('type') == 'ground':
          print('Vegetob density:', round(cell.get('grass').density))
          if cell.get('Herds') != []:
            herds = cell.get('Herds')
            print('****************')
            for herd in herds:
              print(f'Average values of the Herd:')
              avgEnergy = np.average([member.energy for member in listHerd[herd].memberList])
              avgAge = np.average([member.age for member in listHerd[herd].memberList])
              avgSA = np.average([member.socialAttitude for member in listHerd[herd].memberList])
              avgLifetime = np.average([member.lifetime for member in listHerd[herd].memberList])
              print(f'Number of components: {len(listHerd[herd].memberList)}, Energy: {math.ceil(avgEnergy)}, Age: {math.floor(avgAge)}, Social attitude: {math.ceil(avgSA)}, Lifetime: {yearLength*avgLifetime}')
          if cell.get('Prides')!= []:
            prides = cell.get('Prides')
            print('________________')
            for pride in prides:
              print(f'Values of the Erbast:')
              print(pride)
              avgEnergy = np.average([member.energy for member in listPride[pride].memberList])
              avgAge = np.average([member.age for member in listPride[pride].memberList])
              avgSA = np.average([member.socialAttitude for member in listPride[pride].memberList])
              avgLifetime = np.average([member.lifetime for member in listPride[pride].memberList])
              print(f'Number of components: {len(listPride[pride].memberList)}, Energy: {math.ceil(avgEnergy)}, Age: {math.floor(avgAge)}, Social attitude: {math.ceil(avgSA)}, Lifetime: {yearLength*avgLifetime}')
        print('------------------')
      if pygame.mouse.get_pressed()[2] and not gameStarted:
        pos= pygame.mouse.get_pos()
        if(pos[1]//sizeCell != 0 and pos[1]!=9 and pos[0]//sizeCell!=0 and pos[0]//sizeCell!=0):
          cells[pos[1] // sizeCell] [pos[0] // sizeCell] = {"type": 'ground', 'grass': Vegetob(random.randint(0,100)), 'Herds': [], 'Prides': []} if cells[pos[1] // sizeCell] [pos[0] // sizeCell]['type'] == 'water' else {'type': 'water'}
          update(screen, cells, sizeCell)
          pygame.display.flip()
          pygame.display.update()
          time.sleep(0.1)
      
    screen.fill(COLOR_GRID)
if __name__ == "__main__":
  main()
