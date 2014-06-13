from github import Github
import requests

class GithubUser():
  def __init__(self, code=None, token=None, client_id=None, secret=None):
    self.token = token or self.get_token(code, client_id, secret)
    self.g = Github(self.token)
    self.user = self.g.get_user()
    self.orgs = self.user.get_orgs()
    self.repos = self.user.get_repos()
    self.teams = self.user.get_teams()
  def is_valid(self):
    return bool(self.token)
  def get_token(self, code, client_id, secret):
    data = {
    'client_id': client_id,
    'client_secret': secret,
    'code': code
    }
    headers = {'Accept': 'application/json'}
    r = requests.post('https://github.com/login/oauth/access_token', data=data, headers=headers)
    return r.json().get('access_token')
  def verify_org(self, org):
    for o in self.orgs:
      if str(o.id) == org:
        return True
    return False
  def verify_repo(self, repo):
    for t in self.teams:
      for r in list(t.get_repos()) + list(self.repos):
        if str(r.id) == repo:
          return True
    return False
