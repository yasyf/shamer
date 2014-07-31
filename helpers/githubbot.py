from github import Github
from flask import render_template
from jinja2 import TemplateNotFound
import requests

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

  def process_hook(self, pull_request_id, constants, url, args, storage):
    message = constants.get('GH_BOT_MESSAGE')
    ci_restart_url = constants.get('CI_RESTART_URL')
    ci_api_key = constants.get('CI_API_KEY')
    build_id = args.get('build_id')
    if build_id:
      pr = self.repo.get_pull(pull_request_id)
      base_commit_sha = pr.base.sha
      # Sometimes coverage reports do funky things. This should prevent recording most of them.
      rb = float(args.get('ruby', 0)) - float(storage.get('master').get('ruby').get(base_commit_sha)[0])
      js = float(args.get('js', 0)) - float(storage.get('master').get('js').get(base_commit_sha)[0])
      if rb <= -10 or js <= -10:
        commit = self.repo.get_commit(args.get('commit_id')) or pr.get_commits().reversed[0]
        user = storage.get(commit.author.login) or {'name': commit.author.name, 'login': commit.author.login}
        if user.get('dangerously_low') != True:
          user['dangerously_low'] = True
          storage.set(pr.user.login, user)
          url = ci_restart_url.replace('$build_id$', build_id).replace('$api_key$', ci_api_key)
          requests.post(url)
          body = "Something doesn't look right... I'm re-running the coverage reports." \
            + "This comment will be updated when I'm done."
          self.post_comment(body, pr)
          return False
    self.update_leaderboard(pull_request_id, args, storage)
    self.comment(pull_request_id, message, url, args, storage)
    return True

  def update_leaderboard(self, pull_request_id, args, storage):
    if storage.get('master'):
      pr = self.repo.get_pull(pull_request_id)
      base_commit_sha = pr.base.sha
      user = storage.get(pr.user.login) or {'name': pr.user.name, 'login': pr.user.login}
      recorded = user.get('recorded', {})
      contribution = user.get('contribution', {'rb': 0, 'js': 0})
      pull_request_id = str(pull_request_id)
      if pull_request_id in recorded.keys():
        contribution['rb'] -= recorded[pull_request_id]['rb']
        contribution['js'] -= recorded[pull_request_id]['js']
      rb = float(args.get('ruby', 0)) - float(storage.get('master').get('ruby').get(base_commit_sha)[0])
      js = float(args.get('js', 0)) - float(storage.get('master').get('js').get(base_commit_sha)[0])
      recorded[pull_request_id] = {'rb': rb, 'js': js}
      contribution['rb'] += rb
      contribution['js'] += js
      user['contribution'] = contribution
      user['recorded'] = recorded
      user['net_contribution'] = contribution['rb'] + contribution['js']
      user['dangerously_low'] = False
      storage.set(pr.user.login, user)

  def comment(self, pull_request_id, message, url, args, storage):
    pr = self.repo.get_pull(pull_request_id)
    user = storage.get(pr.user.login)
    rank = None
    if user:
      all_users = [x['login'] for x in storage.all({'value.contribution': \
        {'$exists': True}}, ('value.net_contribution', -1))]
      rank = (all_users.index(pr.user.login) + 1, len(all_users))
    try:
      body = render_template('_comment.md', pr=pr, url=url, args=args, storage=storage, rank=rank)
    except TemplateNotFound:
      body = "{}: [{}]({})".format(message, pr.title, url)
    self.post_comment(body, pr)

  def post_comment(self, body, pr):
    past_comment = self.past_comment(pr)
    if past_comment:
      past_comment.edit(body)
    else:
      pr.create_issue_comment(body)

  def get_pr_by_branch(self, branch_name):
    for pull in self.repo.get_pulls(state='open'):
      if pull.head.ref == branch_name:
        return pull
