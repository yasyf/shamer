#github-s3-auth

##What is it?

**TODO**

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

The `jinja2` template at `templates/_comment.md` is how the service generates GitHub comments. We have included a sample that we use for adding code coverage notifiations to pull requests, but you can change this to suit your needs. 
