from github import Github
import requests

class GithubUser():
  def __init__(self, code=None, token=None, client_id=None, secret=None):
    self.token = token or self.get_token(code, client_id, secret)
    self.g = Github(self.token)
    self.user = self.g.get_user()
    self.orgs = self.user.get_orgs()
  def get_token(self, code, client_id, secret):
    data = {
    'client_id': client_id,
    'client_secret': secret,
    'code': code
    }
    headers = {'Accept': 'application/json'}
    r = requests.post('https://github.com/login/oauth/access_token', data=data, headers=headers)
    return r.json()['access_token']
  def verify(self, org):
    for o in self.orgs:
      if o.id == org:
        return True
    return False
