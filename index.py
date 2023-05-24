import random
import numpy as np
import pygame
import time
import os
import math
from grid import createGrid
from settings import *
from vegetob import Vegetob
from animals import Erbast, Carviz
listHerd = []  # listHerd=[istance1, istance2 etc...]
idHerds = []
listPride = []
idPrides = []
cells = createGrid(numCells)


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
                threshold = np.random.normal(60, 10)
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
    for i in range(nErbast):
        xCreature, yCreature, energyCreature, lifetimeCreature, socialAttitudeCreature, idPride = attributeNewAnimal(
            'Erbast')
        Erbast(xCreature, yCreature, energyCreature, lifetimeCreature,
               socialAttitudeCreature, cells, listPride, idPrides, idPride)
    for k in range(nCarviz):
        xCreature, yCreature, energyCreature, lifetimeCreature, socialAttitudeCreature, idHerd = attributeNewAnimal(
            'Carviz')
        Carviz(xCreature, yCreature, energyCreature, lifetimeCreature,
               socialAttitudeCreature, cells, listHerd, idHerds, idHerd)


def update(screen, cells, size):
    if rgbConfiguration:
        for row, col in np.ndindex(cells.shape):
            if (cells[row, col].get('type') == 'water'):
                pygame.draw.rect(screen, (144, 144, 144),
                                 (col*size, row*size, size-1, size-1))
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
                                livingSpecies(listPride)
                        blueIntensity = 255 - round(155*sizePride)
                    if len(herds) > 0:
                        sizeHerd = 0
                        for idHerd in herds:
                            sizeHerd += len(listHerd[idHerd].memberList) / \
                                livingSpecies(listHerd)
                        redIntensity = 255 - round(155*sizeHerd)

                pygame.draw.rect(screen, (redIntensity, greenIntensity,
                                 blueIntensity), (col*size, row*size, size-1, size-1))

    else:
        for row, col in np.ndindex(cells.shape):
            color = COLOR_WATER if cells[row, col].get(
                'type') == 'water' else COLOR_GROUND
            pygame.draw.rect(
                screen, color, (col*size, row*size, size-1, size-1))
            if color == COLOR_GROUND:
                vegetob = cells[row][col].get('grass')
                vegetobSize = 0 if vegetob.density == 0 else vegetob.density / \
                    100*(size-1)
                pygame.draw.rect(screen, COLOR_VEGETOB,
                                 (col*size, row*size, vegetobSize, vegetobSize))
                herds = cells[row][col].get('Herds')
                prides = cells[row][col].get('Prides')
                if len(prides) > 0:
                    for idPride in prides:
                        if (len(listPride[idPride].memberList) > 0):
                            sizePride = len(
                                listPride[idPride].memberList)/livingSpecies(listPride)
                            xRnd = random.randint(
                                1, size-int((0.3*size*sizePride)+(size/5)+2))
                            yRnd = random.randint(
                                1, size-int((0.3*size*sizePride)+(size/5)+2))
                            pygame.draw.rect(screen, (0, 0, 0), (col*size+xRnd-1, row*size+yRnd-1,
                                             (0.3*size*sizePride)+(size/5)+2, (0.3*size*sizePride)+(size/5)+2))
                            pygame.draw.rect(screen, COLOR_PRIDE, (col*size+xRnd, row*size+yRnd,
                                             (0.3*size*sizePride)+(size/5), (0.3*size*sizePride)+(size/5)))
                        # si moltiplica x0.3 perchè al massimo un branco può essere grande 1/2 della cella
                if len(herds) > 0:
                    for idHerd in herds:

                        if (len(listHerd[idHerd].memberList) > 0):
                            sizeHerd = len(
                                listHerd[idHerd].memberList)/livingSpecies(listHerd)
                            xRnd = random.randint(
                                1, size-int((0.3*size*sizeHerd)+(size/5)+2))
                            yRnd = random.randint(
                                1, size-int((0.3*size*sizeHerd)+(size/5)+2))
                            pygame.draw.rect(screen, (0, 0, 0), (col*size+xRnd-1, row*size+yRnd-1,
                                                                 (0.3*size*sizeHerd)+(size/5)+2, (0.3*size*sizeHerd)+(size/5)+2))
                            pygame.draw.rect(screen, COLOR_HERD, (col*size+xRnd, row*size+yRnd,
                                                                  (0.3*size*sizeHerd)+(size/5), (0.3*size*sizeHerd)+(size/5)))


def main():
    global listPride, listHerd, idPrides, idHerds
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
            generateAnimals(10, 10)
            update(screen, cells, sizeCell)
            pygame.display.update()
            firstGeneration = False
            gameStarted = True
        if gameStarted and running:
            for row, col in np.ndindex(cells.shape):
                if cells[row][col]['type'] == 'ground':
                    cells[row][col].get('grass').grow()
                    vegetobKiller(row, col)

            for member in filter(lambda pride: pride is not None, listPride):
                member.decideStrategy(cells, listPride, idPrides)

            # se un Herd deve ancora muoversi e ha un Pride che costretto si è mosso nella sua cella, allora troverà xMov=yMov=0
            for member in filter(lambda herd: herd is not None, listHerd):
                member.decideStrategy(cells, listHerd, idHerds)

            update(screen, cells, sizeCell)
            pygame.display.update()
            # time.sleep(pause)
            joinPrides()
            handleHerds()
            update(screen, cells, sizeCell)
            pygame.display.update()
            # time.sleep(pause)
            hunt()

            for member in filter(lambda pride: pride is not None, listPride):
                member.agingGroup(livingSpecies(listPride),
                                  cells, listPride, idPrides)
            for member in filter(lambda herd: herd is not None, listHerd):
                member.agingGroup(livingSpecies(listHerd),
                                  cells, listHerd, idHerds)
            update(screen, cells, sizeCell)
            pygame.display.update()
            if (livingSpecies(listHerd) == 0):
                print(f'Match lasted {generationCounter} rounds')
                pygame.quit()
                return
            else:
                generationCounter += 1
            idHerds, idPrides, listHerd, listPride = resetIndex(
                idHerds, idPrides, listHerd, listPride)
            # running = not running
            # time.sleep(.1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print(idPrides)
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    update(screen, cells, sizeCell)
                    pygame.display.update()
                    running = not running
            if event.type == pygame.KEYDOWN:
                if (event.key == 115):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print('++++++++++++++++++++++')
                    print('GAME STARTED')
                    print('++++++++++++++++++++++')
                    gameStarted = True
                elif (event.key == 43 and pause < 5):
                    pause += 0.1
                elif (event.key == 45 and pause >= 0.1):
                    pause -= 0.1
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                cell = cells[pos[1] // sizeCell][pos[0] // sizeCell]
                print('Cell of type:', cell.get('type'),
                      '\nCoordinates:', pos[1]//sizeCell, pos[0]//sizeCell)
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
            if pygame.mouse.get_pressed()[2] and not gameStarted:
                pos = pygame.mouse.get_pos()
                if (pos[1]//sizeCell != 0 and pos[1] != 9 and pos[0]//sizeCell != 0 and pos[0]//sizeCell != 0):
                    cells[pos[1] // sizeCell][pos[0] // sizeCell] = {"type": 'ground', 'grass': Vegetob(random.randint(
                        0, 100)), 'Herds': [], 'Prides': []} if cells[pos[1] // sizeCell][pos[0] // sizeCell]['type'] == 'water' else {'type': 'water'}
                    update(screen, cells, sizeCell)
                    pygame.display.flip()
                    pygame.display.update()
                    time.sleep(0.1)

        screen.fill(COLOR_GRID)


if __name__ == "__main__":
    main()
