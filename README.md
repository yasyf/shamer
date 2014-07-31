#Shamer

Shamer is a simple micro-service written in Python with the Flask web framework. The goal of this project is to selectively allow access to code coverage reports hosted on Amazon S3 by authenticating users via GitHub. A user is checked for membership in an organization, and push access to a repository before being allowed to continue on to the coverage reports in S3. This server can either act as a cached proxy for reports served from your bucket, or redirect to signed, expiring URLs that allow your bucket to serve the reports directly.

Additionally, Shamer includes a customizable leaderboard that breaks down cumulative code coverage contrinution by user and language, with a drill-down view that shows how each pull request impacted a user's total.

There is a single webhook which can take any arbitrary parameters and use them to construct a comment to be posted on a GitHub pull request. We use this to post a link to relevant code coverage reports on every PR.

The included deploy script, and features such as cache clearing, depend on this code being deployed to [Heroku](https://www.heroku.com/). If you are deploying to AWS or any other cloud provider, you will probably need to alter the code.

##Deploy Instructions

Install `pip` if you haven't already.

```
$ sudo easy_install pip
```
Clone and deploy your Shamer instance.

```
$ git clone git@github.com:localytics/coverager.git
$ cd coverager
$ sudo pip install requests termcolor
$ ./deploy.py
```

To reuse your config from the last deploy, edit `.env` as needed, then run the deploy script with `foreman` to pre-populate your environment.
```
$ foreman run ./deploy.py
```
##Customization

The jinja2 template at `templates/_comment.md` is how the service generates GitHub comments. We have included a sample that we use for adding code coverage notifiations to pull requests, but you can change this to suit your needs.
