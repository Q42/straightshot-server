import os
import logging
import cloudstorage as gcs
import webapp2
import jinja2
import uuid
import httplib2

from apiclient import discovery
from oauth2client import appengine
from oauth2client import client
from google.appengine.api import memcache
from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.api import images
#from google.appengine.api import users


CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Warning: Please configure OAuth 2.0</h1>
<p>
To make this sample run you will need to populate the client_secrets.json file
found at:
</p>
<p>
<code>%s</code>.
</p>
<p>with information found on the <a
href="https://code.google.com/apis/console">APIs Console</a>.
</p>
""" % CLIENT_SECRETS


service = discovery.build("plus", "v1", http=httplib2.Http(memcache))
decorator = appengine.oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/plus.me',
    message=MISSING_CLIENT_SECRETS_MESSAGE)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        files = File.query().order(-File.createdDate).fetch(10)

        for file in files:
            filename = '/gs/' + app_identity.get_default_gcs_bucket_name()
            filename += '/' + file.key.id() + '.png'
            file.serving_url = images.get_serving_url(None, filename=filename)

        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render({'files': files}))


class ImagesHandler(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write('"ok"')
        logging.info('Uploaded file length: ' + str(len(self.request.body)))

        id = uuid.uuid4().hex
        filename = '/' + app_identity.get_default_gcs_bucket_name()
        filename += '/' + id + '.png'

        gcs_file = gcs.open(filename, 'w', content_type='image/png')
        gcs_file.write(self.request.body)
        gcs_file.close()

        file = File(id=id)
        file.put()

    def options(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST'


class TokenHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        try:
            http = decorator.http()
            user = service.people().get(userId='me').execute(http=http)
            logging.info('displayName: ' + user['displayName'])
            self.response.write(str(user))
        except client.AccessTokenRefreshError:
            self.redirect('/')

        #self.response.headers['Content-Type'] = 'application/json'

        #gae_user = users.get_current_user()
        #if gae_user:
        #    user = User(id=gae_user.user_id(), token=uuid.uuid4().hex, email=gae_user.email())
        #    user.put()
        #    self.response.write(user.token)
        #else:
        #    return webapp2.redirect(users.create_login_url('/token'))


class File(ndb.Model):
    createdDate = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    #userEmail = ndb.StringProperty(indexed=True)
    #userName = ndb.StringProperty(indexed=False)
    # TODO point to a User instead of duplicating email and name fields?


class User(ndb.Model):
    token = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/images', ImagesHandler),
    ('/token', TokenHandler),
    (decorator.callback_path, decorator.callback_handler())
], debug=True)
