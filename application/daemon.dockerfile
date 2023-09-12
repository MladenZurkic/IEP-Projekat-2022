FROM python:3

RUN mkdir -p /opt/src/daemon
WORKDIR /opt/src/daemon

COPY src/daemon.py ./daemon.py
COPY src/models.py ./models.py
COPY src/configuration.py ./configuration.py
COPY src/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt
ENV PYTHONPATH="/opt/src/daemon"

ENTRYPOINT ["python", "./daemon.py"]
