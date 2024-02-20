# ChatCollab v3.2

### To build the docker image
~~~
docker build -f Dockerfile -t chatcollab:latest .
~~~

### Run docker image in same directory as env file
~~~
docker run --env-file .env -p 8000:8000 chatcollab:latest
~~~


To-do:
1. Move slack channel ID to environment variables