from github import Github

class GithubBot():
  def __init__(self, org, repo, token):
    self.g = Github(token)
    self.org = self.g.get_organization(org)
    self.repo = self.org.get_repo(repo)
  
  def comment(self, pull_request_id, message, url):
    pr = self.repo.get_pull(pull_request_id)
    body = "{}: [{}]({})".format(message, pr.title, url)
    pr.create_issue_comment(body)
