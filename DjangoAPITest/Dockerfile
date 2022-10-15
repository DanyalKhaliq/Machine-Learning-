FROM postgres
ENV POSTGRES_PASSWORD danyal123
ENV POSTGRES_DB DjangoAPIdb

RUN pip install --upgrade pip && \
    pip install -r requirements.txt
RUN sudo apt install python3.9

COPY . .
CMD bash setup.sh

## have not tested