Download gcloud:

    https://cloud.google.com/sdk/

Install the Python components:

    gcloud components install app-engine-python

Install virtualenv (not sure if this virtualenv stuff is actually needed but last time I completely broke my Python setup, so better be safe than sorry):

    sudo easy_install pip
    sudo pip install virtualenv

Create an environment:

    cd ..
    virtualenv env

Activate the environment (do this everytime you start working on the project):

    source env/bin/activate

Install dependencies:

    cd straightshot-server
    pip install -t lib -r requirements.txt

Run:

    dev_appserver.py .

Deploy:

    #gcloud preview app deploy app.yaml


To get local image resizing working I had to do:

    sudo pip install pillow
    export PYTHONPATH="/lib/python2.7/site-packages:/usr/local/google_appengine"
