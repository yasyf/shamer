from github import Github
from flask import render_template
from jinja2 import TemplateNotFound

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

  def comment(self, pull_request_id, message, url, args):
    pr = self.repo.get_pull(pull_request_id)
    try:
      body = render_template('_comment.md', pr=pr, url=url, args=args)
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
