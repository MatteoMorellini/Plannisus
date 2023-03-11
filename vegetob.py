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