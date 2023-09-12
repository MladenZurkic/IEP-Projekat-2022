FROM python:3

RUN mkdir -p /opt/src/warehouse
WORKDIR /opt/src/warehouse

COPY src/models.py ./models.py
COPY src/warehouse.py ./warehouse.py
COPY src/configuration.py ./configuration.py
COPY src/requirements.txt ./requirements.txt
COPY src/roleCheckDecorator.py ./roleCheckDecorator.py

RUN pip install -r ./requirements.txt
ENV PYTHONPATH="/opt/src/warehouse"

ENTRYPOINT ["python", "./warehouse.py"]
