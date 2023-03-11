from settings import sizeCell, percentageTowardsCentre
def relativePosition(pos):
  relativePosition = pos / ((600/sizeCell)-2) #perchè se ci sono 10 celle, 2 sono i bordi quindi a noi interessano 8
  rel = percentageTowardsCentre - (relativePosition * percentageTowardsCentre)
  return round(rel, 3)

