#!/usr/bin/env python

import subprocess, os, sys, uuid, re
try:
	from termcolor import colored
except ImportError:
	def colored(msg, color, **kwargs):
		return msg

def call_without_output(cmd):
	return subprocess.call(cmd, stdout=DEVNULL, stderr=DEVNULL)

def prompt(instructions):
	return raw_input(colored(instructions + ": ", 'blue', attrs=['bold']))

def clear():
	subprocess.call('cls' if os.name == 'nt' else 'clear')

def check_for_heroku():
	if call_without_output(['which', 'heroku']) == 1:
		sys.exit(colored('Please install and set up the heroku toolbelt before running this script!', 'red'))
	print colored('Checking your heroku credentials...', 'magenta')
	subprocess.call(['heroku', 'auth:whoami'])
	print
	print colored('Welcome to the github-s3-auth deployer script!', 'green')
	print colored('Please enter the following config vars.', 'green')
	print

def prompt_with_condition(message, condition, error):
	done = False
	while not done:
		inp = prompt(message)
		if not condition(inp):
			print colored(error, 'red')
		else:
			done = True
	return inp

def prompt_need_response(var):
	return prompt_with_condition(var, lambda x: len(x) > 0, 'you must enter a {}'.format(var))

def prompt_with_length(var, length):
	return prompt_with_condition(var, lambda x: len(x) == length, '{} must be {} characters long'.format(var, length))

def get_params():
	APP_NAME = prompt('heroku app name (blank for random)') or ''
	SK = prompt('flask app secret key (blank for random)') or str(uuid.uuid4())

	AWS_BUCKET = prompt_need_response('s3 bucket')
	AWS_ACCESS_KEY = prompt_with_length('aws access key', 20)
	AWS_SECRET_KEY = prompt_with_length('aws secret key', 40)

	GH_ORG_NAME = prompt_need_response('github org name')
	GH_REPO_NAME = prompt_need_response('github repo name')

	print colored('Get your org and repo ids from the GitHub API', 'green')
	GH_ORG = prompt_with_condition('github org id', lambda x: x.isdigit() ,'org id must be an int')
	GH_REPO = prompt_with_condition('github repo id', lambda x: x.isdigit() ,'repo id must be an int')

	print colored('Create a new GitHub App at ', 'green') + colored('https://github.com/organizations/{}/settings/applications'.format(GH_ORG_NAME), 'cyan')
	GH_CLIENT_ID = prompt_with_length('github client id', 20)
	GH_SECRET = prompt_with_length('github client secret', 40)
	
	_locals = locals()
	params = ['APP_NAME', 'SK', 'AWS_BUCKET', 'AWS_ACCESS_KEY', 'AWS_SECRET_KEY','GH_ORG', 'GH_REPO', 'GH_ORG_NAME', 'GH_REPO_NAME', 'GH_CLIENT_ID', 'GH_SECRET']
	return {param:_locals[param] for param in params}

def deploy(params):
	print colored('Creating Heroku App', 'magenta')
	try:
		if params['APP_NAME']:
			output = subprocess.check_output(['heroku', 'create', params['APP_NAME']])
		else:
			output = subprocess.check_output(['heroku', 'create'])
		params['APP_NAME'] = re.match(r'Creating (.*)\.\.\.', output).group(1)
	except subprocess.CalledProcessError:
		sys.exit(colored('heroku app creation failed!', 'red'))
	config = map(lambda x: "{}={}".format(x[0], x[1]), params.items())

	print colored('Writing Heroku Config Vars To .env', 'magenta')
	with open('.env', 'w') as f:
		f.write("\n".join(config))

	print colored('Setting Heroku Config Vars', 'magenta')
	call_without_output(['heroku', 'config:set'] + config + ['--app', params['APP_NAME']])

	print colored('Deploying to Heroku', 'magenta')
	git_remote = 'git@heroku.com:{}.git'.format(params['APP_NAME'])
	call_without_output(['git', 'remote', 'add', params['APP_NAME'], git_remote])
	call_without_output(['git', 'push', params['APP_NAME'], 'master'])

	message = colored("Set your GitHub App's Homepage URL to ", 'green') \
	+ colored("http://{}.herokuapp.com".format(params['APP_NAME']), 'cyan')

	print message
	prompt_with_condition('done? [y/n]', lambda x: x.lower() == 'y', message)

	message = colored("Set your GitHub App's Authorization Callback URL to ", 'green') \
	+ colored("http://{}.herokuapp.com/callback".format(params['APP_NAME']), 'cyan')
	
	print message
	prompt_with_condition('done? [y/n]', lambda x: x.lower() == 'y', message)

	print colored('Launching App!', 'magenta')
	call_without_output(['heroku', 'ps:scale', 'web=1'])
	call_without_output(['heroku', 'apps:open', '--app', params['APP_NAME']])

	print colored('App URL: ', 'green') \
	+ colored('http://{}.herokuapp.com'.format(params['APP_NAME']), 'cyan')

if __name__ == '__main__':
	DEVNULL = open(os.devnull, 'w')
	try:
		clear()
		check_for_heroku()
		params = get_params()
		deploy(params)
	except KeyboardInterrupt:
		sys.exit(colored('\nDeploy cancelled', 'red'))
