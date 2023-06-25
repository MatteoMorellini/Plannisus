import random
import numpy as np
import os
import math
from grid import createGrid
from settings import *
from animals import Erbast, Carviz
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
listHerd = []  # listHerd=[istance1, istance2 etc...]
idHerds = []
listPride = []
idPrides = []
cells = createGrid(numCells)
firstGeneration = True
running = False
generationCounter = 0
populationHistory = {}
toDisplay = 'magenta'


def resetIndex(idHerds, idPrides, listHerd, listPride):
    enumeratedIndex = list(range(len(idHerds)))
    substitute = dict(zip(idHerds, enumeratedIndex))
    idHerds = enumeratedIndex
    for cell in list(cells.flat):
        if cell['type'] == 'ground' and len(cell['Herds']) != 0:
            cell['Herds'] = list(map(lambda x: substitute[x], cell['Herds']))
    enumeratedIndex = list(range(len(idPrides)))
    substitute = dict(zip(idPrides, enumeratedIndex))
    idPrides = enumeratedIndex
    for cell in list(cells.flat):
        if cell['type'] == 'ground' and len(cell['Prides']) != 0:
            cell['Prides'] = list(map(lambda x: substitute[x], cell['Prides']))
    listHerd = [herd for herd in listHerd if herd is not None]
    listPride = [pride for pride in listPride if pride is not None]
    for count, herd in enumerate(listHerd):
        herd.id = count
    for count, pride in enumerate(listPride):
        pride.id = count
    return idHerds, idPrides, listHerd, listPride


def hunt():
    for row, col in np.ndindex(cells.shape):
        if cells[row][col]['type'] == 'ground':
            if (cells[row][col]['Herds'] != [] and cells[row][col]['Prides'] != []):
                idHerd = cells[row][col]['Herds'][0]
                idPride = cells[row][col]['Prides'][0]
                stdHerd = np.std(
                    [member.socialAttitude for member in listHerd[idHerd].memberList])
                stdPride = np.std(
                    [member.socialAttitude for member in listPride[idPride].memberList])
                listHerd[idHerd].memberList.sort(
                    key=lambda member: member.energy, reverse=True)
                lenHerd = len(listHerd[idHerd].memberList)
                listPride[idPride].memberList.sort(
                    key=lambda member: member.energy, reverse=True)
                lenPride = len(listPride[idPride].memberList)
                # utilizzando la funzione list creo una nuova istanza della lista che non fa riferimento alla stessa cella di memoria
                # perchè non vogliamo che la social attitude si sommi poi durante lo svolgimento normale
                newEnergyPredator = [
                    member.energy for member in listHerd[idHerd].memberList]
                newEnergyPrey = [
                    member.energy for member in listPride[idPride].memberList]
                if lenHerd > lenPride:
                    for i in range(lenHerd-lenPride):
                        predatorToJoin = random.randint(0, lenPride)
                        newEnergyPredator[i] = (
                            listHerd[idHerd].memberList[predatorToJoin].energy + listHerd[idHerd].memberList[lenPride+i].energy)
                    numberOfFights = lenPride
                elif lenPride > lenHerd:
                    for i in range(lenPride-lenHerd):
                        preyToJoin = random.randint(0, lenHerd)
                        newEnergyPrey[i] = (
                            listPride[idPride].memberList[preyToJoin].energy + listPride[idPride].memberList[lenHerd+i].energy)
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
                # due casi: i predatori sono più delle prede o le prede sono più dei predatori
                # nel primo caso ordino in ordine decrescente per energia e sommo


def vegetobKiller(row, col):
    subset = list(cells[row-1:row+2, col-1:col+2].flat)
    subset.pop(4)
    subset = [cell for cell in subset if cell.get('type') == 'ground']
    nearFullGrowth = len(
        [cell.get('grass').density for cell in subset if cell.get('grass').density == 100])
    if nearFullGrowth == len(subset)-1 and nearFullGrowth > 1:
        for idPride in cells[row][col]['Prides']:
            listPride[idPride] = None
            idPrides.remove(idPride)
        cells[row][col]['Prides'] = []
    elif nearFullGrowth == len(subset):
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
        if cells[row][col]['type'] == 'ground':
            if len(cells[row][col]['Prides']) > 1:
                cells[row][col]['Prides'].sort(key=lambda idGroup: len(
                    listPride[idGroup].memberList), reverse=True)
                for idGroup in cells[row][col]['Prides'][1:]:
                    listPride[cells[row][col]['Prides'][0]
                              ].memberList += listPride[idGroup].memberList
                    listPride[idGroup] = None
                    cells[row][col]['Prides'].remove(idGroup)
                    idPrides.remove(idGroup)


def handleHerds():
    for row, col in np.ndindex(cells.shape):
        if cells[row][col]['type'] == 'ground':
            numHerds = len(cells[row][col]['Herds'])
            if numHerds > 1:
                cells[row][col]['Herds'].sort(key=lambda idGroup: len(
                    listHerd[idGroup].memberList), reverse=True)
                avgSAHerds = np.average([np.average([carviz.socialAttitude for carviz in listHerd[cells[row]
                                        [col]['Herds'][index]].memberList]) for index in range(len(cells[row][col]['Herds']))])
                threshold = np.random.normal(70, 10)
                if (avgSAHerds < threshold):
                    # se ci sono più di 2 Herds nella stessa casella e abbiamo calcolato che combatteranno allora mettiamo da parte i due
                    # gruppi più numerosi e gli altri li trattiamo nel seguente modo:
                    # se la std è bassa si uniranno tutti i componenti allo stesso gruppo scelto a caso tra i due, altrimenti saranno coinvolti nello scontro rimanendo nella stessa orda
                    if numHerds > 2:
                        minorHerdsId = cells[row][col]['Herds'][2:]
                        for minorHerdId in minorHerdsId:
                            stdHerdSA = np.std(
                                [member.socialAttitude for member in listHerd[minorHerdId].memberList])
                            if (stdHerdSA < 20):
                                majorGroupToJoin = random.randint(0, 1)
                                listHerd[cells[row][col]['Herds'][majorGroupToJoin]
                                         ].memberList += listHerd[minorHerdId].memberList
                                listHerd[minorHerdId] = None
                                idHerds.remove(minorHerdId)
                                cells[row][col]['Herds'].remove(minorHerdId)
                                numHerds -= 1
                    while numHerds > 1:
                        fightingHerd1 = listHerd[cells[row][col]['Herds'][0]]
                        if len(fightingHerd1.memberList) > 1:
                            fightingHerd1.memberList.sort(
                                key=lambda member: member.energy, reverse=True)
                        fightingHerd2 = listHerd[cells[row][col]['Herds'][1]]
                        if len(fightingHerd2.memberList) > 1:
                            fightingHerd2.memberList.sort(
                                key=lambda member: member.energy, reverse=True)
                        while True:
                            if (fightingHerd1.memberList[0].energy-fightingHerd2.memberList[0].energy > 0):
                                fightingHerd1.memberList[0].energy -= fightingHerd2.memberList[0].energy
                                fightingHerd2.memberList.pop(0)
                                if (fightingHerd2.memberList == []):
                                    numHerds -= 1
                                    listHerd[cells[row][col]
                                             ['Herds'][1]] = None
                                    idHerds.remove(cells[row][col]['Herds'][1])
                                    cells[row][col]['Herds'].pop(1)
                                    break
                            else:
                                fightingHerd2.memberList[0].energy -= fightingHerd1.memberList[0].energy
                                fightingHerd1.memberList.pop(0)
                                if (fightingHerd1.memberList == []):
                                    numHerds -= 1
                                    listHerd[cells[row][col]
                                             ['Herds'][0]] = None
                                    idHerds.remove(cells[row][col]['Herds'][0])
                                    cells[row][col]['Herds'].pop(0)
                                    break
                else:
                    for idGroup in cells[row][col]['Herds'][1:]:
                        listHerd[cells[row][col]['Herds'][0]
                                 ].memberList += listHerd[idGroup].memberList
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
    xCreature = random.randint(1, numCells-1)
    yCreature = random.randint(1, numCells-1)
    while (cells[yCreature][xCreature]['type'] != 'ground'):
        xCreature = random.randint(1, numCells-1)
        yCreature = random.randint(1, numCells-1)
    if sort == 'Erbast' and cells[yCreature][xCreature]['Prides'] != []:
        idGroup = cells[yCreature][xCreature]['Prides'][0]
    elif sort == 'Carviz' and cells[yCreature][xCreature]['Herds'] != []:
        idGroup = cells[yCreature][xCreature]['Herds'][0]
    energyCreature = int(np.random.normal(60, 10))
    while energyCreature < 0 or energyCreature > 100:
        energyCreature = int(np.random.normal(60, 10))
    lifetimeCreature = int(random.randint(2, 6))
    socialAttitudeCreature = int(np.random.normal(50, 20))
    while socialAttitudeCreature < 0 or socialAttitudeCreature > 100:
        socialAttitudeCreature = int(np.random.normal(50, 20))
    return xCreature, yCreature, energyCreature, lifetimeCreature, socialAttitudeCreature, idGroup


def generateAnimals(nErbast, nCarviz):
    for _ in range(nErbast):
        xCreature, yCreature, energyCreature, lifetimeCreature, socialAttitudeCreature, idPride = attributeNewAnimal(
            'Erbast')
        Erbast(xCreature, yCreature, energyCreature, lifetimeCreature,
               socialAttitudeCreature, cells, listPride, idPrides, idPride)
    for _ in range(nCarviz):
        xCreature, yCreature, energyCreature, lifetimeCreature, socialAttitudeCreature, idHerd = attributeNewAnimal(
            'Carviz')
        Carviz(xCreature, yCreature, energyCreature, lifetimeCreature,
               socialAttitudeCreature, cells, listHerd, idHerds, idHerd)


def buttonPressed(event):
    if event.button == 1 and event.inaxes == ax1:  # Clic sinistro del mouse
        # Ottenimento delle coordinate del punto cliccato
        x, y = event.xdata, event.ydata
        cell = cells[math.floor(y*numCells)][math.floor(x*numCells)]
        print('Cell of type:', cell.get('type'),
              '\nCoordinates:', math.floor(y*numCells), math.floor(x*numCells))
        if cell.get('type') == 'ground':
            print('Vegetob density:', round(cell.get('grass').density))
            if cell.get('Herds') != []:
                herds = cell.get('Herds')
                print('****************')
                for herd in herds:
                    print(f'Average values of the Herd:')
                    avgEnergy = np.average(
                        [member.energy for member in listHerd[herd].memberList])
                    avgAge = np.average(
                        [member.age for member in listHerd[herd].memberList])
                    avgSA = np.average(
                        [member.socialAttitude for member in listHerd[herd].memberList])
                    avgLifetime = np.average(
                        [member.lifetime for member in listHerd[herd].memberList])
                    print(
                        f'Number of components: {len(listHerd[herd].memberList)}, Energy: {math.ceil(avgEnergy)}, Age: {math.floor(avgAge)}, Social attitude: {math.ceil(avgSA)}, Lifetime: {math.ceil(yearLength*avgLifetime)}')
            if cell.get('Prides') != []:
                prides = cell.get('Prides')
                print('________________')
                for pride in prides:
                    print(f'Values of the Erbast:')
                    print(pride)
                    avgEnergy = np.average(
                        [member.energy for member in listPride[pride].memberList])
                    avgAge = np.average(
                        [member.age for member in listPride[pride].memberList])
                    avgSA = np.average(
                        [member.socialAttitude for member in listPride[pride].memberList])
                    avgLifetime = np.average(
                        [member.lifetime for member in listPride[pride].memberList])
                    print(
                        f'Number of components: {len(listPride[pride].memberList)}, Energy: {math.ceil(avgEnergy)}, Age: {math.floor(avgAge)}, Social attitude: {math.ceil(avgSA)}, Lifetime: {math.ceil(yearLength*avgLifetime)}')
        print('------------------')
    elif event.button == 3 and event.inaxes == ax1:
        x, y = event.xdata, event.ydata
        cell = cells[math.floor(y*numCells)][math.floor(x*numCells)]
        if cell.get('type') == 'ground':
            if cell.get('Herds') != []:
                herds = cell.get('Herds')
                for i, herd in enumerate(listHerd):
                    if i in herds:
                        herd.tracking = not herd.tracking
                    else:
                        herd.tracking = False
            if cell.get('Prides') != []:
                prides = cell.get('Prides')
                for i, pride in enumerate(listPride):
                    if i in prides:
                        pride.tracking = not pride.tracking
                    else:
                        pride.tracking = False


def keyPressed(event):
    global running, interval, toDisplay
    if (event.key == 'enter'):

        if (generationCounter == 0):
            os.system('cls' if os.name == 'nt' else 'clear')
            print('++++++++++++++++++++++')
            print('GAME STARTED')
            print('++++++++++++++++++++++')
        running = True
    elif event.key == ' ':
        running = False
    elif event.key == 'e':
        toDisplay = 'blue'
    elif event.key == 'c':
        toDisplay = 'red'
    elif event.key == 'a':
        toDisplay = 'magenta'


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
cid = fig.canvas.mpl_connect('button_press_event', buttonPressed)
cid = fig.canvas.mpl_connect('key_press_event', keyPressed)
fig.suptitle('Day: 0')
ax1.axis('off')


def createScreen(cells):
    populationPride = livingSpecies(listPride)
    populationHerd = livingSpecies(listHerd)
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
                    for idPride in prides:

                        sizePride += len(listPride[idPride].memberList) / \
                            populationPride
                    blueIntensity = 255 - round(155*sizePride)
                if len(herds) > 0:
                    sizeHerd = 0
                    for idHerd in herds:
                        sizeHerd += len(listHerd[idHerd].memberList) / \
                            populationHerd
                    redIntensity = 255 - round(155*sizeHerd)
        cells[row, col]['draw'] = plt.Rectangle((col/numCells, row/numCells), 1/numCells, 1/numCells, facecolor=(
            redIntensity/255, greenIntensity/255, blueIntensity/255, 1))
        ax1.add_patch(cells[row, col]['draw'])


def updateScreen(cells, counter):
    global populationHistory
    populationPride = livingSpecies(listPride)
    populationHerd = livingSpecies(listHerd)
    for row, col in np.ndindex(cells.shape):
        if (cells[row, col].get('type') == 'water'):
            continue
        else:
            cellTracked = False
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
                    for idPride in prides:
                        group = listPride[idPride]
                        if group.tracking:
                            cells[row][col]['tracked'] = 5
                            cellTracked = True
                        sizePride += len(group.memberList) / \
                            populationPride
                    blueIntensity = 255 - round(155*sizePride)
                if len(herds) > 0:
                    sizeHerd = 0
                    for idHerd in herds:
                        group = listHerd[idHerd]
                        if group.tracking:
                            cells[row][col]['tracked'] = 5
                            cellTracked = True
                        sizeHerd += len(group.memberList) / \
                            populationHerd
                    redIntensity = 255 - round(155*sizeHerd)
        if redIntensity != 0 or blueIntensity != 0:
            cells[row, col]['draw'].set_facecolor(
                (redIntensity/255, greenIntensity/255, blueIntensity/255, 1))
        elif cells[row][col]['tracked'] > 0 and not cellTracked:
            cells[row][col]['tracked'] -= 1
            cells[row, col]['draw'].set_facecolor(
                (1, 1, 0, 1))
        else:
            cells[row, col]['draw'].set_facecolor(
                (redIntensity/255, greenIntensity/255, blueIntensity/255, 1))

    ax2.cla()
    populationHistory[generationCounter] = ((populationPride, populationHerd))
    if generationCounter > 100:
        del populationHistory[generationCounter-100]
    if toDisplay == 'blue':
        populationToDisplay = [generation[0]
                               for generation in populationHistory.values()]
    elif toDisplay == 'red':
        populationToDisplay = [generation[1]
                               for generation in populationHistory.values()]
    else:
        populationToDisplay = [generation[0]+generation[1]
                               for generation in populationHistory.values()]
    ax2.plot(list(populationHistory.keys()),
             populationToDisplay, color=toDisplay)
    fig.suptitle(f'Day: {generationCounter}')


def update(frame):
    global firstGeneration, running, cells, listPride, idPrides, listHerd, idHerds, generationCounter
    if firstGeneration:
        generateAnimals(10, 10)
        firstGeneration = False
        createScreen(cells)
    if running:
        for row, col in np.ndindex(cells.shape):
            if cells[row][col]['type'] == 'ground':
                cells[row][col].get('grass').grow()
                vegetobKiller(row, col)

        for member in filter(lambda pride: pride is not None, listPride):
            member.decideStrategy(cells, listPride, idPrides)
        # se un Herd deve ancora muoversi e ha un Pride che costretto si è mosso nella sua cella, allora troverà xMov=yMov=0
        for member in filter(lambda herd: herd is not None, listHerd):
            member.decideStrategy(cells, listHerd, idHerds)

        joinPrides()
        handleHerds()
        hunt()

        for member in filter(lambda pride: pride is not None, listPride):
            member.agingGroup(livingSpecies(listPride),
                              cells, listPride, idPrides)
        for member in filter(lambda herd: herd is not None, listHerd):
            member.agingGroup(livingSpecies(listHerd),
                              cells, listHerd, idHerds)
        if (livingSpecies(listHerd) == 0):
            print(f'Match lasted {generationCounter} rounds')
            plt.close()
            anim.event_source.stop()

        else:
            generationCounter += 1
            idHerds, idPrides, listHerd, listPride = resetIndex(
                idHerds, idPrides, listHerd, listPride)
            updateScreen(cells, generationCounter)


anim = FuncAnimation(fig, update, interval=500)
plt.show()
