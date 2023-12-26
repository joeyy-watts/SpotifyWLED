FROM python:3.9

COPY ./app /usr/src/app

WORKDIR /usr/src/app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
EXPOSE 8081

CMD [ "python", "main.py" ]