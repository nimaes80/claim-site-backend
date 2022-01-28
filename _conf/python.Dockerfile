ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}-alpine

ARG USER_ID
ARG GROUP_ID
ARG USER_NAME
ARG SERVER_PORT

RUN apk add sudo 

RUN addgroup -g ${GROUP_ID} ${USER_NAME}  && \
    adduser -h /home/${USER_NAME} -s /bin/ash ${USER_NAME} -u ${USER_ID} -D -G ${USER_NAME}  ${USER_NAME}  && \
    echo "${USER_NAME} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/${USER_NAME} && \
    chmod 0440 /etc/sudoers.d/${USER_NAME} && \
    mkdir -p \
    /home/${USER_NAME} /.vscode-server \
    /home/${USER_NAME} /.vscode-server-insiders \
    /home/${USER_NAME} /.cache && \
    chown -R ${USER_NAME}:${USER_NAME}  /home/${USER_NAME}

WORKDIR /home/${USER_NAME}/app

RUN chown -R ${USER_NAME}:${USER_NAME} /home/${USER_NAME}/app

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8

RUN apk upgrade --update && \
    apk add --no-cache \
    build-base \
    g++ \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    openssl-dev \
    libressl-dev \
    libffi-dev \
    git \
    nano \
    python3-dev \ 
    postgresql-dev \
    gettext && \
    pip install --upgrade pip && \
    pip install --no-cache-dir pipenv

ENV PIPENV_DONT_LOAD_ENV=1

EXPOSE ${SERVER_PORT}

RUN pipenv install && rm Pipfile Pipfile.lock

VOLUME ["/home/${USER_NAME}/app", "/home/${USER_NAME}/.cache", "/home/${USER_NAME}/.local/share/virtualenvs/app_packages"]

USER ${USER_NAME}

RUN sudo chmod -R a+rwx /home/${USER_NAME}/app && \
    sudo chmod -R a+rwx /home/${USER_NAME}/.local && \
    sudo chmod -R a+rwx /home/${USER_NAME}/.cache

CMD exec /bin/sh -c "trap : TERM INT; (while true; do sleep 1000; done) & wait"
