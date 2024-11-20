FROM locustio/locust
LABEL maintainer="charles.burnett@mongodb.com"
LABEL version="1.0.7"

WORKDIR /tmp/locust 
COPY ./locustfile.py ./
COPY ./requirements.txt ./
RUN pip3 install -r requirements.txt
EXPOSE 8089 