FROM python:3.7

WORKDIR /

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
COPY .env .env
COPY /moviesproject/ .

RUN pip install pipenv
RUN pipenv install --deploy --system
