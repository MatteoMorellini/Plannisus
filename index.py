from animals import Erbast, Carviz
from settings import *
from grid import createGrid
from cloud import Cloud
import math
import os
import numpy as np
import random
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import copy

cells = createGrid(numCells)
cellsColor = [[None] * numCells for _ in range(numCells)]
cellsColor = np.array([[None for x in range(numCells)] for y in range(numCells)])
clouds = []
firstGeneration = True
running = False
generationCounter = 0
populationHistory = {}
saHistory = {}
ltHistory = {}
primaryColor = [1, 0, 1]
secondaryColor = [155/255, 0, 155/255]
meteorMode = False
ax2Title = 'Total Population'
ax3Title = 'General Stats'
livingCarviz=0
livingErbast = 0


def hunt():
    global livingErbast
    for row, col in np.ndindex(cells.shape):
        if cells[row][col]['type'] == 'ground':
            if (cells[row][col]['Herds'] != [] and cells[row][col]['Prides'] != []):
                herd = cells[row][col]['Herds'][0]
                pride = cells[row][col]['Prides'][0]
                stdHerd = np.std(
                    [member.socialAttitude for member in herd.memberList])
                stdPride = np.std(
                    [member.socialAttitude for member in pride.memberList])
                herd.memberList.sort(
                    key=lambda member: member.energy, reverse=True)
                lenHerd = len(herd.memberList)
                pride.memberList.sort(
                    key=lambda member: member.energy, reverse=True)
                lenPride = len(pride.memberList)
                # utilizzando la funzione list creo una nuova istanza della lista che non fa riferimento alla stessa cella di memoria
                # perchè non vogliamo che la social attitude si sommi poi durante lo svolgimento normale
                newEnergyPredator = [
                    member.energy for member in herd.memberList]
                newEnergyPrey = [
                    member.energy for member in pride.memberList]
                if lenHerd > lenPride:
                    for i in range(lenHerd-lenPride):
                        predatorToJoin = random.randint(0, lenPride)
                        newEnergyPredator[i] = (
                            herd.memberList[predatorToJoin].energy + herd.memberList[lenPride+i].energy)
                    numberOfFights = lenPride
                elif lenPride > lenHerd:
                    for i in range(lenPride-lenHerd):
                        preyToJoin = random.randint(0, lenHerd)
                        newEnergyPrey[i] = (
                            pride.memberList[preyToJoin].energy + pride.memberList[lenHerd+i].energy)
                    numberOfFights = lenHerd
                else:
                    numberOfFights = lenPride
                for i in range(numberOfFights):
                    if newEnergyPredator[i]-stdHerd > newEnergyPrey[i]-stdPride:
                        herd.feed(newEnergyPrey[i])
                    else:
                        herd.feed(newEnergyPrey[i]-(stdPride-20))
                livingErbast -= len(pride.memberList)
                cells[row][col]['Prides'].remove(pride)                # due casi: i predatori sono più delle prede o le prede sono più dei predatori
                # nel primo caso ordino in ordine decrescente per energia e sommo


def vegetobKiller(row, col):
    global livingCarviz, livingErbast
    subset = list(cells[row-1:row+2, col-1:col+2].flat)
    subset.pop(4)
    subset = [cell for cell in subset if cell.get('type') == 'ground']
    nearFullGrowth = len(
        [cell.get('grass').density for cell in subset if cell.get('grass').density == 100])
    if nearFullGrowth == len(subset)-1 and nearFullGrowth > 1:
        for pride in cells[row,col]['Prides']:
            livingErbast -= len(pride.memberList)
        cells[row][col]['Prides'] = []
    elif nearFullGrowth == len(subset):
        for pride in cells[row,col]['Prides']:
            livingErbast -= len(pride.memberList)
        for herd in cells[row,col]['Herds']:
            livingCarviz -= len(herd.memberList)
        cells[row][col]['Herds'] = []
        cells[row][col]['Prides'] = []

def drawGraph2(livingErbast, livingCarviz):
    ax2.cla()
    ax2.set_title(ax2Title)

    populationHistory[generationCounter] = ((livingErbast, livingCarviz))
    if generationCounter > 100 and not meteorMode:
        del populationHistory[generationCounter-100]
    if primaryColor == [0, 0, 1]:
        populationToDisplay = [generation[0]
                               for generation in populationHistory.values()]
    elif primaryColor == [1, 0, 0]:
        populationToDisplay = [generation[1]
            for generation in populationHistory.values()]
    else:
        populationToDisplay = [generation[0]+generation[1] for generation in populationHistory.values()]

    ax2.plot(list(populationHistory.keys()),
             populationToDisplay, color=primaryColor)

"""def drawGraph3():
    global ax3Display, ax4Display
    saCarviz = saErbast = 0
    ltCarviz = ltErbast = 0
    for member in filter(lambda pride: pride is not None, listPride):
        partialAvgSA = avgValue(member.memberList, 'socialAttitude')
        partialAvgLF = avgValue(member.memberList, 'lifetime')
        if saErbast == 0 or partialAvgSA == 0:
            saErbast += partialAvgSA
        else:
            saErbast = (saErbast + partialAvgSA) / 2
        if ltErbast == 0 or partialAvgLF == 0:
            ltErbast += partialAvgLF
        else:
            ltErbast = (ltErbast + partialAvgLF) / 2
    for member in filter(lambda herd: herd is not None, listHerd):
        partialAvgSA = avgValue(member.memberList, 'socialAttitude')
        partialAvgLF = avgValue(member.memberList, 'lifetime')
        if saCarviz == 0 or partialAvgSA == 0:
            saCarviz += partialAvgSA
        else:
            saCarviz = (saCarviz + partialAvgSA) / 2
        if ltCarviz == 0 or partialAvgLF == 0:
            ltCarviz += partialAvgLF
        else:
            ltCarviz = (ltCarviz + partialAvgLF) / 2
    saHistory[generationCounter] = (int(saCarviz), int(saErbast))
    ltHistory[generationCounter] = (int(ltCarviz), int(ltErbast))
    if primaryColor == [0, 0, 1]:
        ax3Display = [generation[1] for generation in saHistory.values()]
        ax4Display = [generation[1] for generation in ltHistory.values()]
    elif primaryColor == [1, 0, 0]:
        ax3Display = [generation[0] for generation in saHistory.values()]
        ax4Display = [generation[0] for generation in ltHistory.values()]
    else:
        ax3Display = [generation[0]+generation[1] for generation in saHistory.values()]
        ax4Display = [generation[0]+generation[1] for generation in ltHistory.values()]
    ax3.cla()
    ax4.cla()
    ax3.set_title(ax3Title)
    ax3.plot(list(saHistory.keys()), ax3Display, color=secondaryColor)
    ax3.set_ylabel('Average social attitude', color=secondaryColor)
    ax4.set_ylabel('Average life expectancy', color=primaryColor)
    ax4.plot(list(ltHistory.keys()), ax4Display, color=primaryColor)
"""
def joinPrides():
    for row, col in np.ndindex(cells.shape):
        if cells[row][col]['type'] == 'ground':
            if len(cells[row][col]['Prides']) > 1:
                cells[row][col]['Prides'].sort(key=lambda group: len(
                    group.memberList), reverse=True)
                for group in cells[row][col]['Prides'][1:]:
                    cells[row][col]['Prides'][0].memberList += group.memberList
                    cells[row][col]['Prides'].remove(group)


def handleHerds():
    global livingCarviz
    for row, col in np.ndindex(cells.shape):
        if cells[row][col]['type'] == 'ground':
            numHerds = len(cells[row][col]['Herds'])
            if numHerds > 1:
                cells[row][col]['Herds'].sort(key=lambda group: len(
                    group.memberList), reverse=True)
                avgSAHerds = np.average([np.average([carviz.socialAttitude for carviz in group.memberList]) for group in cells[row][col]['Herds']])
                threshold = np.random.normal(70, 10)
                if (avgSAHerds < threshold):
                    # se ci sono più di 2 Herds nella stessa casella e abbiamo calcolato che combatteranno allora mettiamo da parte i due
                    # gruppi più numerosi e gli altri li trattiamo nel seguente modo:
                    # se la std è bassa si uniranno tutti i componenti allo stesso gruppo scelto a caso tra i due, altrimenti saranno coinvolti nello scontro rimanendo nella stessa orda
                    if numHerds > 2:
                        minorHerds = cells[row][col]['Herds'][2:]
                        for minorHerd in minorHerds:
                            stdHerdSA = np.std(
                                [member.socialAttitude for member in minorHerd.memberList])
                            if (stdHerdSA < 20):
                                majorGroupToJoin = random.randint(0, 1)
                                cells[row][col]['Herds'][majorGroupToJoin].memberList += minorHerd.memberList
                                cells[row][col]['Herds'].remove(minorHerd)
                                numHerds -= 1
                    while numHerds > 1:
                        fightingHerd1 = cells[row][col]['Herds'][0]
                        if len(fightingHerd1.memberList) > 1:
                            fightingHerd1.memberList.sort(
                                key=lambda member: member.energy, reverse=True)
                        fightingHerd2 = cells[row][col]['Herds'][1]
                        if len(fightingHerd2.memberList) > 1:
                            fightingHerd2.memberList.sort(
                                key=lambda member: member.energy, reverse=True)
                        while True:
                            if (fightingHerd1.memberList[0].energy-fightingHerd2.memberList[0].energy > 0):
                                fightingHerd1.memberList[0].energy -= fightingHerd2.memberList[0].energy
                                fightingHerd2.memberList.pop(0)
                                livingCarviz-=1
                                if (fightingHerd2.memberList == []):
                                    numHerds -= 1
                                    cells[row][col]['Herds'].pop(1)
                                    break
                            else:
                                fightingHerd2.memberList[0].energy -= fightingHerd1.memberList[0].energy
                                fightingHerd1.memberList.pop(0)
                                livingCarviz-=1
                                if (fightingHerd1.memberList == []):
                                    numHerds -= 1
                                    cells[row][col]['Herds'].pop(0)
                                    break
                else:
                    for group in cells[row][col]['Herds'][1:]:
                        cells[row][col]['Herds'][0].memberList += group.memberList
                        cells[row][col]['Herds'].remove(group)


def attributeNewAnimal():
    xCreature = random.randint(1, numCells-1)
    yCreature = random.randint(1, numCells-1)
    while (cells[yCreature][xCreature]['type'] != 'ground'):
        xCreature = random.randint(1, numCells-1)
        yCreature = random.randint(1, numCells-1)
    energyCreature = int(np.random.normal(60, 10))
    while energyCreature < 0 or energyCreature > 100:
        energyCreature = int(np.random.normal(60, 10))
    lifetimeCreature = int(random.randint(2, 6))
    socialAttitudeCreature = int(np.random.normal(50, 20))
    while socialAttitudeCreature < 0 or socialAttitudeCreature > 100:
        socialAttitudeCreature = int(np.random.normal(50, 20))
    return xCreature, yCreature, energyCreature, lifetimeCreature, socialAttitudeCreature


def generateAnimals(nErbast, nCarviz):
    global livingCarviz, livingErbast
    livingCarviz+=nCarviz
    livingErbast += nErbast
    for _ in range(nErbast):
        xCreature, yCreature, energyCreature, lifetimeCreature, socialAttitudeCreature = attributeNewAnimal()
        Erbast(yCreature, xCreature, energyCreature, lifetimeCreature,
               socialAttitudeCreature, cells)
    for _ in range(nCarviz):
        xCreature, yCreature, energyCreature, lifetimeCreature, socialAttitudeCreature = attributeNewAnimal()
        Carviz(yCreature, xCreature, energyCreature, lifetimeCreature,
               socialAttitudeCreature, cells)


def generateCataclysm(yCell, xCell, cells):
    global livingCarviz, livingErbast
    dimension = random.randint(1, 3)
    carvizKilled = 0
    erbastKilled = 0
    for row in range(-dimension, dimension+1):
        for col in range(-dimension, dimension+1):
            if yCell+row > -1 and yCell+row < numCells and xCell+col > -1 and xCell+col < numCells:
                if cells[yCell+row][xCell + col]['type'] == 'ground':
                    for herd in cells[yCell+row][xCell + col]['Herds']:
                        carvizKilled += len(herd.memberList)
                        
                    #cells[yCell+row][xCell + col]['Herds'] = []
                    for pride in cells[yCell+row][xCell + col]['Prides']:
                        erbastKilled += len(pride.memberList)
                    #cells[yCell+row][xCell + col]['Prides'] = []
                cells[yCell+row][xCell + col] = {'type': 'water','damaged': 3}
    livingCarviz -= carvizKilled
    erbastKilled -= erbastKilled
    print(
        f'A catastrophic meteorite impact has killed {carvizKilled} carviz and {erbastKilled} erbast')


def buttonPressed(event):
    global meteorMode
    if event.inaxes == ax1:
        x, y = event.xdata, event.ydata
        xCell, yCell = math.floor(x*numCells), math.floor(y*numCells)
        cell = cells[yCell][xCell]
        if event.button == 1 and meteorMode == True:
            generateCataclysm(yCell, xCell, cells)
            updateScreen(cells)
            meteorMode = False
        elif event.button == 1:  # Clic sinistro del mouse
            # Ottenimento delle coordinate del punto cliccato
            print('Cell of type:', cell.get('type'),
                  '\nCoordinates:', yCell, xCell)
            if cell.get('type') == 'ground':
                print('Vegetob density:', round(cell.get('grass').density))
                if cell.get('Herds') != []:
                    herds = cell.get('Herds')
                    print('****************')
                    for herd in herds:
                        print(f'Average values of the Herd:')
                        avgEnergy = np.average(
                            [member.energy for member in herd.memberList])
                        avgAge = np.average(
                            [member.age for member in herd.memberList])
                        avgSA = np.average(
                            [member.socialAttitude for member in herd.memberList])
                        avgLifetime = np.average(
                            [member.lifetime for member in herd.memberList])
                        print(
                            f'Number of components: {len(herd.memberList)}, Energy: {math.ceil(avgEnergy)}, Age: {math.floor(avgAge)}, Social attitude: {math.ceil(avgSA)}, Lifetime: {math.ceil(yearLength*avgLifetime)}')
                if cell.get('Prides') != []:
                    prides = cell.get('Prides')
                    print('________________')
                    for pride in prides:
                        print(f'Values of the Erbast:')
                        print(pride)
                        avgEnergy = np.average(
                            [member.energy for member in pride.memberList])
                        avgAge = np.average(
                            [member.age for member in pride.memberList])
                        avgSA = np.average(
                            [member.socialAttitude for member in pride.memberList])
                        avgLifetime = np.average(
                            [member.lifetime for member in pride.memberList])
                        print(
                            f'Number of components: {len(pride.memberList)}, Energy: {math.ceil(avgEnergy)}, Age: {math.floor(avgAge)}, Social attitude: {math.ceil(avgSA)}, Lifetime: {math.ceil(yearLength*avgLifetime)}')
            print('------------------')
        elif event.button == 3:
            if cell.get('type') == 'ground':
                if cell.get('Herds') != []:
                    herds = cell.get('Herds')
                    for herd in herds:
                        herd.tracking = not herd.tracking
                if cell.get('Prides') != []:
                    prides = cell.get('Prides')
                    for pride in prides:
                            pride.tracking = not pride.tracking


def keyPressed(event):
    global running, interval, primaryColor, secondaryColor, meteorMode, ax2Title, ax3Title
    if (event.key == 'enter'):
        running = True
        meteorMode = False
    elif event.key == ' ':
        running = False
    elif event.key == 'e':
        primaryColor = [0, 0, 1]
        ax2Title = 'Erbast Population'
        ax3Title = 'Erbast Stats'
        secondaryColor = [0, 0, 155/255]
    elif event.key == 'c':
        primaryColor = [1, 0, 0]
        ax2Title = 'Carviz Population'
        ax3Title = 'Carviz Stats'
        secondaryColor = [155/255, 0, 0]
    elif event.key == 'a':
        primaryColor = [1, 0, 1]
        ax2Title = 'Total Population'
        ax3Title = 'General Stats'
        secondaryColor = [155/255, 0, 155/255]
    elif event.key == 'm' and running == False:
        meteorMode = not meteorMode
        print('\u2604 \u26A0 METEOR MODE ACTIVATED \u26A0 \u2604')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
cid = fig.canvas.mpl_connect('button_press_event', buttonPressed)
cid = fig.canvas.mpl_connect('key_press_event', keyPressed)
fig.suptitle('Day: 0')
ax1.axis('off')
ax1.set_title('Map')
ax2.set_title(ax2Title)
#ax3.set_title(ax3Title)
#ax4 = ax3.twinx()  # instantiate a second axes that shares the same x-axis

def avgValue(group, value):
    return sum(getattr(animal, value) for animal in group)/len(group) if len(group) > 0 else 0


def createScreen(cells):
    for row, col in np.ndindex(cells.shape):
        if (cells[row, col].get('type') == 'water'):
            blueIntensity = greenIntensity = redIntensity = 144
        else:
            redIntensity = greenIntensity = blueIntensity = 0
            herds = cells[row][col].get('Herds')
            prides = cells[row][col].get('Prides')
            if (len(herds) == 0 and len(prides) == 0):
                vegetob = cells[row][col].get('grass')
                greenIntensity = 255 if vegetob.density == 0 else 255 - \
                    155*(vegetob.density/100)
            else:
                if len(prides) > 0:
                    sizePride = 0
                    for pride in prides:
                        sizePride += len(pride.memberList) / livingErbast
                    blueIntensity = 255 - round(155*sizePride)
                if len(herds) > 0:
                    sizeHerd = 0
                    for herd in herds:
                        sizeHerd += len(herd.memberList) / livingCarviz
                    redIntensity = 255 - round(155*sizeHerd)
        cellsColor[row][col] = plt.Rectangle((col/numCells, row/numCells), 1/numCells, 1/numCells, facecolor=(
            redIntensity/255, greenIntensity/255, blueIntensity/255, 1))
        ax1.add_patch(cellsColor[row][col])


def updateScreen(cells):
    global populationHistory
    for row, col in np.ndindex(cells.shape):
        cell = cells[row, col]
        if any((row,col) in cloud.coords for cloud in clouds):
            redIntensity = 204
            greenIntensity = 229
            blueIntensity = 255
        elif (cell.get('type') == 'water'):
            if 'damaged' in cell:
                if cell['damaged'] > 0:
                    cell['damaged'] -= 1
                    redIntensity = 155 + int(100*random.random())
                    greenIntensity = int(123*random.random())
                    blueIntensity = 0
                else:
                    blueIntensity = greenIntensity = redIntensity = 144
                    del cell['damaged']
            else:
                blueIntensity = greenIntensity = redIntensity = 144
        else:
            cellTracked = False
            redIntensity = greenIntensity = blueIntensity = 0
            herds = cell.get('Herds')
            prides = cell.get('Prides')
            if (len(herds) == 0 and len(prides) == 0):
                vegetob = cell.get('grass')
                greenIntensity = 255 if vegetob.density == 0 else 255 - \
                    155*(vegetob.density/100)
            else:
                if len(prides) > 0:
                    sizePride = 0
                    for pride in prides:
                        pride.visited = False
                        if pride.tracking:
                            cells[row][col]['tracked'] = 5
                            cellTracked = True
                        sizePride += len(pride.memberList) / livingErbast
                    blueIntensity = 255 - round(155*sizePride)
                if len(herds) > 0:
                    sizeHerd = 0
                    for herd in herds:
                        herd.visited = False
                        if herd.tracking:
                            cells[row][col]['tracked'] = 5
                            cellTracked = True
                        sizeHerd += len(herd.memberList) / livingCarviz
                    redIntensity = 255 - round(155*sizeHerd)
        if redIntensity != 0 or blueIntensity != 0:
            cellsColor[row][col].set_facecolor(
                (redIntensity/255, greenIntensity/255, blueIntensity/255, 1))
        elif cells[row][col]['tracked'] > 0 and not cellTracked:
            cellsColor[row][col].set_facecolor(
                (1, 1, (5-cells[row][col]['tracked'])*51/255, 1))
            cells[row][col]['tracked'] -= 1
            
        else:
            cellsColor[row][col].set_facecolor(
                (redIntensity/255, greenIntensity/255, blueIntensity/255, 1))
    drawGraph2(livingErbast, livingCarviz)
    #if generationCounter%10==0:
        #drawGraph3()
    fig.suptitle(f'Day: {generationCounter}')

def update(frame):
    global firstGeneration, running, cells, generationCounter, livingCarviz, livingErbast
    if firstGeneration:
        generateAnimals(10, 10)
        firstGeneration = False
        createScreen(cells)
        if (generationCounter == 0):
            os.system('cls' if os.name == 'nt' else 'clear')
            print('++++++++++++++++++++++')
            print('GAME STARTED')
            print('++++++++++++++++++++++')
    if running:
        modifiedCells = copy.deepcopy(cells)
        for row, col in np.ndindex(cells.shape):
            cell = cells[row][col]
            modifiedCell = modifiedCells[row][col]
            if cell['type'] == 'ground':
                for cloud in clouds:
                    if (row,col) in cloud.coords:
                        modifiedCell.get('grass').extremeGrow()
                        break
                else:
                    modifiedCell.get('grass').grow()
                vegetobKiller(row, col)
                for pride in modifiedCell['Prides']:
                    if not pride.visited:
                        pride.decideStrategy(cells, modifiedCells, row, col)
                        if pride in cell['Prides']:
                            livingErbast += pride.agingGroup(livingErbast, modifiedCells)
                for herd in modifiedCell['Herds']:
                    if not herd.visited:
                        herd.decideStrategy(modifiedCells, row, col)
                        if herd in cell['Herds']:
                            livingCarviz += herd.agingGroup(livingCarviz,modifiedCells)
        if random.random() < 0.005: #cataclysm
            xCell, yCell = math.floor(
                random.random()*numCells), math.floor(random.random()*numCells)
            generateCataclysm(yCell, xCell, modifiedCells)
        for cloud in clouds:
            cloud.move()
            if len(cloud.coords) == 0:
                clouds.remove(cloud)
        if random.random() < 0.02:
            xCell, yCell = math.floor(
                random.random()*numCells), math.floor(random.random()*numCells)
            clouds.append(Cloud(yCell, xCell))            
        
        cells = modifiedCells

        joinPrides()
        handleHerds()
        hunt()
        
        if (livingCarviz == 0):
            print(f'Match lasted {generationCounter} rounds')
            plt.close()
            anim.event_source.stop()

        else:
            generationCounter += 1
            updateScreen(modifiedCells)
anim = FuncAnimation(fig, update, interval=0)
plt.show()
plt.tight_layout()
