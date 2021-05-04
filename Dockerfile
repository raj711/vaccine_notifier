FROM python:3.7

RUN mkdir /vaccine_finder

WORKDIR /vaccine_finder

ADD ./requirements.txt  ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONUNBUFFERED 0

COPY . .

EXPOSE 8080

CMD ["gunicorn","--bind","0.0.0.0:8080","--workers","2","--timeout", "7200", "app:app"]