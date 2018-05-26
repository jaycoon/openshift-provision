FROM pipenv-python3

COPY . /webapp
WORKDIR /webapp

RUN pipenv install --system --deploy

EXPOSE 8000
VOLUME /webapp

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
