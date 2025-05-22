FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt update
RUN apt install gcc python3-dev build-essential libev-dev libffi-dev bash python-is-python3 -y

COPY requirements.txt /app
RUN python -m pip install -U pip
RUN python -m pip install wheel setuptools
RUN python -m pip install -r requirements.txt

COPY *.py /app/

ENV PYTHONUNBUFFERED 1
ENTRYPOINT ["python3"]
CMD ["server.py"]
