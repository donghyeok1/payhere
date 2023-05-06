FROM python:3.9
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY . /app
RUN pip install -r requirements.txt