from github import Github
import requests

class GithubUser():
  def __init__(self, code=None, token=None):
    self.token = token or self.get_token(code)
    self.g = Github(self.token)
    self.user = self.g.get_user()
    self.orgs = self.user.get_orgs()
  def get_token(self, code):
    data = {
    'client_id': constants.get('GH_CLIENT_ID'),
    'client_secret': constants.get('GH_SECRET'),
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
