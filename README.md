# ChatCollab v3.2

### To build the docker image
~~~
docker build -f Dockerfile -t chatcollab:latest .
~~~

### Run docker image in same directory as env file
~~~
docker run --env-file .env -p 8000:8000 -p 8080:8080 chatcollab:latest
~~~


GUIDE:
When done using ChatCollab, please follow these steps as best practice:
1. Export Slack messages then delete them from the channel, so there are no messages in the channel.
2. Refresh your tab of the ChatCollab admin page, which will clear all existing agent threads.
3. Close all tabs of the ChatCollab admin page. When using ChatCollab, only have one tab open at a time.
