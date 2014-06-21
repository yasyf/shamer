from github import Github
from flask import render_template
from jinja2 import TemplateNotFound
from helpers.constants import Constants

class GithubBot():
  def __init__(self, org, repo, token, storage=None):
    self.g = Github(token)
    self.user = self.g.get_user()
    self.org = self.g.get_organization(org)
    self.repo = self.org.get_repo(repo)
  
  def past_comment(self, pr):
    for comment in pr.get_issue_comments():
      if comment.user.id == self.user.id:
        return comment

  def update_leaderboard(self, pull_request_id, args, storage):
    pr = self.repo.get_pull(pull_request_id)
    user = storage.get(pr.user.login) or {'name': pr.user.name, 'login': pr.user.login}
    recorded = user.get('recorded', [])
    if pull_request_id not in recorded:
      recorded.append(pull_request_id)
      contribution = user.get('contribution', {'rb': 0, 'js': 0})
      contribution['rb'] += (float(args.get('ruby', 0)) - float(storage.get('master')['ruby'][0]))
      contribution['js'] += (float(args.get('js', 0)) - float(storage.get('master')['js'][0]))
      user['contribution'] = contribution
      user['recorded'] = recorded
      storage.set(pr.user.login, user)

  def comment(self, pull_request_id, message, url, args, storage):
    pr = self.repo.get_pull(pull_request_id)
    try:
      body = render_template('_comment.md', pr=pr, url=url, args=args, storage=storage)
    except TemplateNotFound:
      body = "{}: [{}]({})".format(message, pr.title, url)
    past_comment = self.past_comment(pr)
    if past_comment:
      past_comment.edit(body)
    else:
      pr.create_issue_comment(body)

  def get_pr_by_branch(self, branch_name):
    for pull in self.repo.get_pulls(state='open'):
      if pull.head.ref == branch_name:
        return pull
