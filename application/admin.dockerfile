FROM python:3

RUN mkdir -p /opt/src/admin
WORKDIR /opt/src/admin

COPY src/models.py ./models.py
COPY src/admin.py ./admin.py
COPY src/configuration.py ./configuration.py
COPY src/requirements.txt ./requirements.txt
COPY src/roleCheckDecorator.py ./roleCheckDecorator.py

RUN pip install -r ./requirements.txt
ENV PYTHONPATH="/opt/src/admin"

ENTRYPOINT ["python", "./admin.py"]
