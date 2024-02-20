# ChatCollab v3.2

### To build the docker image
~~~
docker build -f Dockerfile -t chatcollab:latest .
~~~

### Run docker image in same directory as env file
~~~
docker run --env-file .env -p 8000:8000 -p 8080:8080 chatcollab:latest
~~~


To-do:
1. Try GPT3 instead of GPT4 and see results
2. Add feature to export OpenAI calls
3. Bring online 