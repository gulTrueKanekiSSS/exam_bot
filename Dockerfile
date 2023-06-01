FROM python:3.10

WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
COPY docker_config.py default_config.py
CMD python3 bot.py