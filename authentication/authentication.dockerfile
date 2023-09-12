FROM python:3


RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication


COPY src/models.py ./models.py
COPY src/application.py ./application.py
COPY src/configuration.py ./configuration.py
COPY src/requirements.txt ./requirements.txt
COPY src/adminDecorator.py ./adminDecorator.py


RUN pip install -r ./requirements.txt
ENV PYTHONPATH="/opt/src/authentication"


ENTRYPOINT ["python", "./application.py"]
