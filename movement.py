import random
from settings import percentageTowardsCentre

def relativeMovement(rel):
  randomNumber = random.random()
  if(randomNumber <= 0.3): #la possibilità che rimanga ferma è del 30% non variabile
    addPos = 0
  elif(randomNumber > 0.3 and randomNumber < 0.65-(percentageTowardsCentre/2)+rel): 
    #la percentuale massima del movimento in avanti è 35% dato che se ptc è 0 allora avremo sempre 35 (questo però non accade)
    #la pts è anche il valore massimo che può assumere rel, perciò togliamo da ambo le parti metà di ptc
    addPos = 1
  else:
    addPos = -1
  return addPos