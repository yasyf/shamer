class Constants():
  def __init__(self, source):
    # Dictionary-like object
    self.source = source
    # Defaults
    self.defaults = {'EXPIRES': 300, 'GH_SCOPE': 'user,repo,read:org'}
  def get(self, key):
    return self.source.get(key) or self.defaults.get(key)
  def set(self, key, value):
    self.source[key] = value
