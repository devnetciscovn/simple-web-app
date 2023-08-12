FROM ubuntu
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-flask
COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt
COPY flaskr /flaskr
WORKDIR /flaskr
CMD flask run --host=0.0.0.0