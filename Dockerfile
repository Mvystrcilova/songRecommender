FROM python:3.7

WORKDIR /usr/src/app

COPY Pipfile ./

RUN pip install pipenv

RUN pipenv install --skip-lock

COPY . .

EXPOSE 80

CMD ["./entrypoint.sh"]
