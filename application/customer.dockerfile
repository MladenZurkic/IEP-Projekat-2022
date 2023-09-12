FROM python:3

RUN mkdir -p /opt/src/customer
WORKDIR /opt/src/customer

COPY src/models.py ./models.py
COPY src/customer.py ./customer.py
COPY src/configuration.py ./configuration.py
COPY src/requirements.txt ./requirements.txt
COPY src/roleCheckDecorator.py ./roleCheckDecorator.py

RUN pip install -r ./requirements.txt
ENV PYTHONPATH="/opt/src/customer"

ENTRYPOINT ["python", "./customer.py"]
