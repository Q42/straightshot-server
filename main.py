import os
import logging
import cloudstorage as gcs
import webapp2
import jinja2
import uuid

from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.api import images

class MainPage(webapp2.RequestHandler):
    def get(self):
        files = File.query().order(-File.createdDate).fetch(10)

        for file in files:
            filename = '/gs/' + app_identity.get_default_gcs_bucket_name()
            filename += '/' + file.key.id() + '.png'
            file.serving_url = images.get_serving_url(None, filename=filename)

        template = JINJA_ENVIRONMENT.get_template('templates/index.html')
        self.response.write(template.render({'files': files}))


class Images(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write('"ok"')
        logging.info('Uploaded file length: ' + str(len(self.request.body)))

        id = str(uuid.uuid4())
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


class File(ndb.Model):
    createdDate = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    userEmail = ndb.StringProperty(indexed=True)
    userName = ndb.StringProperty(indexed=False)


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/images', Images)
], debug=True)
