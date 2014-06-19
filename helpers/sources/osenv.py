import os

class OSConstants():
  def __init__(self):
    self.store = os.environ

  def get(self, key):
    return self.store.get(key)

  def set(self, key, value):
    self.store[key] = value
