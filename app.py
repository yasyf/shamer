from flask import Flask, redirect, session, request, render_template, url_for, flash, jsonify, g
from helpers.s3 import S3
from helpers.constants import Constants
from helpers.githubuser import GithubUser
from helpers.githubbot import GithubBot
import os, time

app = Flask(__name__)
dev = os.environ.get('dev') == 'true' or not os.environ.get('PORT')
constants = Constants(os.environ)
app.secret_key = constants.get('SK')
try:
  s3 = S3(constants.get('AWS_ACCESS_KEY'), constants.get('AWS_SECRET_KEY'), constants.get('AWS_BUCKET'))
except:
  s3 = None

try:
  bot = GithubBot(constants.get('GH_ORG_NAME'), constants.get('GH_REPO_NAME'), constants.get('GH_BOT_TOKEN'))
except:
  bot = None

@app.before_request
def preprocess_request():
  if request.endpoint in {'redirect_view', 'proxy_view', 'pending_view', 'go_view'}:
    if session.get('verified') != True:
      return redirect(url_for('login_view'))
    if not s3:
      flash('Your S3 keys are invalid!', 'danger')
      return redirect(url_for('demo_view'))
    g.object_key = request.args.get('object_key')
    if not g.object_key:
      flash('No object key was set!', 'danger')
      return redirect(url_for('demo_view'))
    session['object_key'] = g.object_key

@app.after_request
def postprocess_request(response):
  if not dev:
    response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000')
  return response

@app.route('/')
def index_view():
  return redirect(url_for('demo_view'))

@app.route('/redirect')
def redirect_view():
  url = s3.get_url(g.object_key, int(constants.get('EXPIRES')), force_http=constants.get('HTTP') == 'true')
  return redirect(url if url else url_for('pending_view', object_key=g.object_key))

@app.route('/proxy')
def proxy_view():
  f = s3.get_file(g.object_key)
  return f.read()

@app.route('/go')
def go_view():
  return redirect(url_for('{}_view'.format(constants.get('MODE')), object_key=g.object_key))

@app.route('/pending')
def pending_view():
  return render_template('pending.html', object_key=g.object_key, bucket=constants.get('AWS_BUCKET'))

@app.route('/login')
def login_view():
  session['state'] = str(hash(str(time.time())+constants.get('SK')))
  query = 'client_id={}&scope={}&state={}'.format(
    constants.get('GH_CLIENT_ID'),
    constants.get('GH_SCOPE'),
    session['state'])
  return redirect('https://github.com/login/oauth/authorize?{}'.format(query))

@app.route('/callback')
def callback_view():
  if request.args.get('state') == session.get('state'):
    code = request.args.get('code')
    user = GithubUser(code=code, client_id=constants.get('GH_CLIENT_ID'), secret=constants.get('GH_SECRET'))
    if user.is_valid():
      session['token'] = user.token
      if user.verify_org(constants.get('GH_ORG')) and user.verify_repo(constants.get('GH_REPO')):
        flash('You are now logged in!', 'success')
        session['verified'] = True
      else:
        flash('You do not satisfy the authentication requirements!', 'danger')
        session['verified'] = False
    else:
      flash('Your GitHub credentials are not valid!', 'danger')
      session['verified'] = False
  if session.get('object_key'):
    object_key = session.pop('object_key')
    return redirect(url_for('redirect_view', object_key=object_key))
  return redirect(url_for('demo_view'))

@app.route('/hook/<pull_request_id>')
def hook_view(pull_request_id):
  object_key = request.args.get('object_key')
  if not object_key:
    return jsonify({'status': 'no object_key'})
  if bot:
    if not pull_request_id.isdigit():
      try:
        # pull_request_id is the branch name
        pull_request_id = bot.get_pr_by_branch(pull_request_id).number
      except:
        return jsonify({'status': 'no such pull request'})
    url = url_for('go_view', object_key=object_key, _external=True)
    message = constants.get('GH_BOT_MESSAGE')
    bot.comment(int(pull_request_id), message, url)
    return jsonify({'status': 'success'})
  return jsonify({'status': 'no bot credentials'})

@app.route('/demo')
def demo_view():
  if session.get('token'):
    return render_template('demo_user.html',
      user=GithubUser(token=session.get('token')),
      v_org=(constants.get('GH_ORG_NAME'), constants.get('GH_ORG')),
      v_repo=(constants.get('GH_REPO_NAME'), constants.get('GH_REPO')))
  else:    
    return render_template('demo.html')

if __name__ == '__main__':
  if dev:
    app.run(host='0.0.0.0', port=5000, debug=True)
  else:
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT')), debug=False)
