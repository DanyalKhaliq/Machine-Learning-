FROM python:3.7
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN gcc --version
RUN apt-get update
RUN apt-get -qq -y install curl
RUN apt-get -y install python3-dev
RUN apt-get -y install unixodbc-dev
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get -y install msodbcsql17
RUN pip3 install -r requirements.txt
COPY . .
CMD streamlit run app.py
#ENTRYPOINT ["streamlit","run", "--server.enableCORS", "false" ,"--server.port", "$PORT"]
#CMD ["app.py"]