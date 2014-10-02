#Shamer

Shamer is a simple micro-service with the goal of making it dead simple to gamify code coverage. Testing is a huge part of our culture at Localytics, and Shamer is the result of our efforts to encourage everyone to write the most thorough tests possible.

Shamer allows you to generate coverage reports (we do this after every successful build), host them in a central location, and automatically comment on Pull Requests with a link to the hosted reports. The rest of that comment is where things get interesting. By allowing you to send coverage data to a single endpoint, Shamer keeps track of aggregate deltas on a per-user and per-commit basis, building a multi-repo leaderboard of each person's contributions over time. Every comment lets the owner of the PR know what their rank is on the leaderboard, and how their code is changing coverage project-wide.

Shamer's guts are an app written in Python with the Flask web framework. It selectively allows access to code coverage reports hosted on Amazon S3 by authenticating users via GitHub. A user is checked for membership in an organization, and push access to a repository before being allowed to continue on to the coverage reports in S3. This server can either act as a cached proxy for reports served from your bucket, or redirect to signed, expiring URLs that allow your bucket to serve the reports directly.

Additionally, Shamer includes templates for a customizable leaderboard that breaks down cumulative code coverage contribution by user and language, with a drill-down view that shows how each pull request impacted a user's total.

There is a single webhook which can take any arbitrary parameters and use them to construct a comment to be posted on a GitHub pull request. Your only external responsibility in setting up Shamer is to notify this hook whenever reports are generated, sending along some relevant metadata about the commit.

The included deploy script depend on this code being deployed to [Heroku](https://www.heroku.com/). If you are deploying to AWS or any other cloud provider, you will probably need to alter the code.

##Deploy Instructions

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/localytics/shamer/)

Click the above button to deploy a Shamer instance to Heroku.

###Manual Deploy

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

##Usage

Once you have a Shamer instance up and running, it is very easy to integrate the leaderboard into your project. In setting up Shamer, you only have one responsibiliy: generate code coverage and pass the numbers to a webhook. How you do this will vary by project and language. At Localytics, we generate coverage after every CI build.

To submit your coverage percentages to Shamer, make a GET request to the `/hook/<pull_request_id>/<path:object_key>` endpoint. The `pull_request_id` is either the number of the PR, or the name of the branch for that PR. The `object_key` is the path to the coverage report on your S3 bucket. You must also include the following query parameters.

- `repo_name`: The name of your GitHub repository
- `build_id`: A unique identifier, often provided by your CI system
- `commit_id`: The commit hash that these coverage percentages are for

The final query parameters are the percentages of coverage for each language, identified by the comma-separated file extensions you entered during setup.

Here is an example request for a project that has both Ruby and JavaScript code, where `my_repo` is the `repo_name`, `123` is the `pull_request_id`, and `xyz/coverage/index.html` is the `object_key`.

```
GET http://shamer.herokuapp.com/hook/123/xyz/coverage/index.html?repo_name=my_repo&build_id=1861574&commit_id=9a98f3bb8dbe23e60f1c1bfb2191a242910b2ea1&js=33.66&rb=57.68
```

##Customization

The jinja2 template at `templates/_comment.md` is how the service generates GitHub comments. We have included a sample that we use for adding code coverage notifiations to pull requests, but you can change this to suit your needs.

There are various other features of Shamer, such as multi-repo support and the ability to restart builds on your CI provider, which can be enabled through environment variables. See [the sample .env file](./.env.sample) for more details.
