FROM docker.io/library/fedora:28

RUN \
    dnf install -y \
        openssh-clients \
        python \
        python-pip \
        python-devel \
        which

RUN \
    pip install --upgrade pip \
    && pip install pipenv==2018.5.18 \
    && dnf clean all

COPY . /app
WORKDIR /app

RUN pipenv install --system --deploy --pre

VOLUME /app
ENTRYPOINT ["/app/entrypoint.sh"]
