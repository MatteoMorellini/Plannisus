import numpy as np
import pygame
import time
COLOR_BG = (10,10,10)
COLOR_GRID = (40,40,40)
COLOR_DIE_NEXT = (170, 170,170)
COLOR_ALIVE_NEXT = (255,255,255)
def update(screen, cells, size, with_progress=False):
  updated_cells = np.array([[cell(row, col, 0) for col in range(80)] for row in range(60)]) 
  for row, col in np.ndindex(cells.shape):
    subset = cells[row-1:row+2, col-1:col+2]
    nearCellsAlive = sum(cell.alive for cell in subset.flat) - cells[row,col].alive
    color = COLOR_BG if cells[row, col].alive == 0 else COLOR_ALIVE_NEXT
    if cells[row,col].alive == 1:
      if nearCellsAlive<2 or nearCellsAlive>3:
        if with_progress:
          color= COLOR_DIE_NEXT
      elif 2<= nearCellsAlive <= 3:
        updated_cells[row, col].alive = 1
        if with_progress:
          color = COLOR_ALIVE_NEXT
    else:
      if nearCellsAlive==3:
        updated_cells[row,col].alive = 1
        if with_progress:
          color = COLOR_ALIVE_NEXT
    pygame.draw.rect(screen, color, (col*size, row*size, size-1, size-1))
  return updated_cells

class cell: 
  def __init__(self, col, row, alive):
    self.col = col
    self.row = row
    self.alive = alive

def main():
  pygame.init()
  screen = pygame.display.set_mode((800,600))
  cells = np.array([[cell(row, col, 0) for col in range(80)] for row in range(60)]) 
  screen.fill(COLOR_GRID)
  update(screen, cells, 10)
  pygame.display.flip()
  pygame.display.update()
  running = False
  while True: 
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        return
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
          running = not running
          update(screen,cells, 10)
          pygame.display.update()
      if pygame.mouse.get_pressed()[0]:
        pos= pygame.mouse.get_pos()
        cells[pos[1] // 10, pos[0] // 10].alive = 1
        update(screen,cells, 10)
        pygame.display.update()
    screen.fill(COLOR_GRID)
    if running: 
      cells = update(screen, cells, 10, with_progress = True)
      pygame.display.update()
      time.sleep(5)
if __name__ == "__main__":
  main()
