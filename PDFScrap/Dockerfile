FROM python:3.8.1-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get -y install libgtk2.0-dev
#RUN apt update
RUN ACCEPT_EULA=Y apt-get -y install ghostscript
RUN pip3 install camelot-py[cv]
RUN pip3 install -r requirements.txt
COPY . .
CMD sh server-debug.sh
