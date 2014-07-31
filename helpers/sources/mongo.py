from pymongo import MongoClient

class MongoConstants():
  def __init__(self, collection_name, mongo_uri):
    self.client = MongoClient(mongo_uri)
    db = mongo_uri.split('/')[-1]
    self.collection = self.client[db][collection_name]

  def get(self, key):
    try:
      return self.collection.find_one({'key': key})['value']
    except (AttributeError,TypeError):
      return None

  def set(self, key, value):
    self.collection.update({'key': key}, {'$set': {'value': value}}, upsert=True)

  def all(self, constraint, sort):
    return [x.get('value') for x in self.collection.find(constraint).sort(*sort)]
