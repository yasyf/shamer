import yaml, requests, itertools

class LanguageExtensions():
  def __init__(self):
    data = requests.get('https://raw.githubusercontent.com/github/linguist/master/lib/linguist/languages.yml')
    languages = yaml.load(data.text)
    extension_mappings = map(lambda (l, x): [(e,l) for e in x.get('extensions', [])], languages.iteritems())
    self.d = dict(itertools.chain(*extension_mappings))
  def get_language_from_extension(self, ext):
    return self.d.get('.' + ext, ext)
