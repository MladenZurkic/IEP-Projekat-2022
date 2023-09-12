FROM python:3


RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication


COPY src/models.py ./models.py
COPY src/migrate.py ./migrate.py
COPY src/configuration.py ./configuration.py
COPY src/requirements.txt ./requirements.txt


RUN pip install -r ./requirements.txt


ENTRYPOINT ["python", "./migrate.py"]
