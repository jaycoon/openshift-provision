FROM docker.io/library/fedora:27

RUN \
    dnf install -y \
        python3 \
        python3-pip \
        python3-devel \
        which \
    && \
    pip3 install pipenv


COPY . /webapp
WORKDIR /webapp


RUN pipenv install --system --deploy

EXPOSE 8000
VOLUME /webapp

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
