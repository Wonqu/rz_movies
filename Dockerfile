FROM python:3 AS default
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN mkdir /code
WORKDIR /code
COPY ./app /code/
COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

FROM default AS test
COPY ./requirements-test.txt /code/requirements-test.txt
RUN pip install -r requirements-test.txt

FROM default as prod
COPY ./requirements-prod.txt /code/requirements-prod.txt
RUN pip install -r requirements-prod.txt
CMD gunicorn movies.wsgi:application --chdir /code/ --bind 0.0.0.0:$PORT --reload