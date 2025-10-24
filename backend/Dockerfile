FROM python:3.11

WORKDIR /api

RUN apt-get update && apt-get install -y netcat-openbsd

COPY ./requirements.txt ./

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

EXPOSE 8000

CMD ["bash", "./run.sh"]