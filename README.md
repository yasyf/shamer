#github-s3-auth

`github-s3-auth` is a simple micro-service written in Python with the Flask web framework. The one and only goal of this project is to allow access to restricted content hosted/stored on Amazon S3 by authenticating users via GitHub. A user is checked for membership in an organization, and push access to a repository before being allowed to continue on to the files in S3. This server can either act as a cached proxy for files served from your bucket, or redirect to signed, expiring URLs that allow your bucket to serve the files directly. Internally, this service is used by Localytics to proxy code coverage reports stored on S3.

As an added bonus, we added a single webhook which can take any arbitrary parameters and use them to construct a comment to be posted on a GitHub pull request. We use this to post a link to relevant code coverage reports on every PR.

##Deploy Instructions

Install `pip` if you haven't already.

```
$ sudo easy_install pip
```
Clone and deploy your `github-s3-auth` instance.

```
$ git clone git@github.com:localytics/github-s3-auth.git
$ cd github-s3-auth
$ sudo pip install requests termcolor
$ ./deploy.py
```

To reuse your config from the last deploy, edit `.env` as needed, then run the deploy script with `foreman` to pre-populate your environment.
```
$ foreman run ./deploy.py
```
##Customization

The jinja2 template at `templates/_comment.md` is how the service generates GitHub comments. We have included a sample that we use for adding code coverage notifiations to pull requests, but you can change this to suit your needs. 
