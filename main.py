import logging
import cloudstorage as gcs
import webapp2

from google.appengine.api import app_identity


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write('Hello World!')


class Images(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.write('"ok"')
        logging.info('Uploaded file length: ' + str(len(self.request.body)))

        filename = '/' + app_identity.get_default_gcs_bucket_name() + '/testje.png'

        gcs_file = gcs.open(filename, 'w', content_type='image/png')
        gcs_file.write(self.request.body)
        gcs_file.close()

    def options(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST'

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/images', Images)
], debug=True)
