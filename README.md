To get the dependencies once:

    pip install -t lib -r requirements.txt


To run:

    gcloud preview app run app.yaml


To deploy:

    gcloud preview app deploy app.yaml


To get local image resizing working I had to do:

    sudo pip install pillow
    export PYTHONPATH="/lib/python2.7/site-packages:/usr/local/google_appengine"
