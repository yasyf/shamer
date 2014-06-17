from github import Github

class GithubBot():
  def __init__(self, org, repo, token, storage=None):
    self.g = Github(token)
    self.org = self.g.get_organization(org)
    self.repo = self.org.get_repo(repo)
    # list-like object, could be persistent
    self.commented = storage if storage else []
  
  def comment(self, pull_request_id, message, url):
    if pull_request_id not in self.commented:
      self.commented.append(pull_request_id)
      pr = self.repo.get_pull(pull_request_id)
      body = "{}: [{}]({})".format(message, pr.title, url)
      pr.create_issue_comment(body)

  def get_pr_by_branch(self, branch_name):
    for pull in self.repo.get_pulls(state='open'):
      if pull.head.ref == branch_name:
        return pull
