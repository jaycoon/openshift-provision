FROM pipenv-python3

COPY . /app

WORKDIR /app
RUN pipenv install --system --deploy

EXPOSE 8000
VOLUME /app

WORKDIR /app/webapp
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
