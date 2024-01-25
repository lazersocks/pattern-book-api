Run: 
docker compose run django  
This will build the image and download any images which are not installed. This api relies on the following images: python, redis and celery.

To get everything running run:
docker compose up 

After this, in a new terminal enter the following command:
docker exec -it book_api /bin/bash

And run migrations 
python manage.py migrate

Now you are able to use the API. 
Note: For the sake of this demo I have not used any env for sensitive information.
