from flask import Flask, redirect, session, request, render_template, url_for, flash
from helpers.s3 import S3
from helpers.constants import Constants
from helpers.githubuser import GithubUser
import os, time

app = Flask(__name__)
dev = os.environ.get('dev') == 'true' or not os.environ.get('PORT')
constants = Constants(os.environ)
app.secret_key = constants.get('SK')
try:
  s3 = S3(constants.get('AWS_ACCESS_KEY'), constants.get('AWS_SECRET_KEY'), constants.get('AWS_BUCKET'))
except:
  s3 = None

@app.before_request
def preprocess_request():
  if request.endpoint in {'redirect_view', 'pending_view'}:
    if session.get('verified') != True:
     return redirect(url_for('login_view'))

@app.after_request
def postprocess_request(response):
  if not dev:
    response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000')
  return response

@app.route('/')
def index_view():
  return redirect(url_for('demo_view'))

@app.route('/redirect/<object_key>')
def redirect_view(object_key):
  session['object_key'] = object_key
  if s3:
    url = s3.get_url(object_key, constants.get('EXPIRES'))
    return redirect(url if url else url_for('pending_view', object_key=object_key))
  else:
    flash('Your S3 keys are invalid!', 'danger')
    return redirect(url_for('demo_view'))

@app.route('/pending/<object_key>')
def pending_view(object_key):
  return render_template('pending.html', object_key=object_key, bucket=constants.get('AWS_BUCKET'))

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
  return redirect(url_for('demo_view'))

@app.route('/demo')
def demo_view():
  if session.get('token'):
    if session.get('object_key'):
      flash("Redirecting to '{}' on S3...".format(session.pop('object_key')), 'warning')
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
