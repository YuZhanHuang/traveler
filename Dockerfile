# Base Config
ARG PYTHON_VERSION=3.9.15
FROM python:${PYTHON_VERSION}-slim as base

# Builder
FROM base as builder

WORKDIR /src/app

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=1.2.*

RUN export DEBIAN_FRONTEND=noninteractive \
  && apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && python -m venv ${POETRY_HOME} \
  && ${POETRY_HOME}/bin/pip install poetry==${POETRY_VERSION} \
  && ${POETRY_HOME}/bin/poetry export --with dev > requirements.txt \
  && pip install --no-cache-dir --disable-pip-version-check --no-warn-script-location --user -r requirements.txt \
  && apt-get clean autoclean \
  && apt-get autoremove --yes \
  && rm -rf /var/lib/{apt,dpkg,cache,log}/

# App
FROM base

ARG USER=flask

ENV HOME=/home/${USER}
ENV PATH=${HOME}/.local/bin:${PATH}

RUN export DEBIAN_FRONTEND=noninteractive \
  && apt-get update \
  && apt-get install -y --no-install-recommends gettext \
  && useradd -s /bin/bash -m -d ${HOME} ${USER} \
  && mkdir ${HOME}/project \
  && mkdir ${HOME}/project/media \
  && chown -R ${USER}:${USER} ${HOME}/project

WORKDIR ${HOME}/project

USER ${USER}

VOLUME ${HOME}/project/media

COPY --chown=${USER}:${USER} --from=builder /root/.local ${HOME}/.local
COPY --chown=${USER}:${USER} docker_entrypoint/service/entrypoint.sh /usr/local/bin/run-server
COPY --chown=${USER}:${USER} . .

RUN chmod +x /usr/local/bin/run-server /usr/local/bin/run-server

EXPOSE 5000
CMD ["run-server"]