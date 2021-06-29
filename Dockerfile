ARG PYTHON_VERSION="3.8"
FROM python:${PYTHON_VERSION} AS base

WORKDIR /usr/src/app

# Install poetry for dep management
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH="$PATH:/root/.poetry/bin"
RUN poetry config virtualenvs.create false

# Install project manifest
COPY pyproject.toml .

# Install poetry.lock from which to build
COPY poetry.lock .

# Install production dependencies
RUN poetry install --no-dev
COPY poetry.lock .

############
# Unit Tests
#
# This test stage runs true unit tests (no outside services) at build time, as
# well as enforcing codestyle and performing fast syntax checks. It is built
# into an image with docker-compose for running the full test suite.
FROM base AS test

# Install full dependencies
RUN poetry install

# Copy in the application source and everything not explicitly banned by
# .dockerignore
COPY . .

# Simple tests
RUN echo 'Running Flake8' && \
    flake8 . && \
    echo 'Running Black' && \
    black --check --diff . && \
    echo 'Running Pylint' && \
    find . -name '*.py' | xargs pylint  && \
    echo 'Running Yamllint' && \
    yamllint . && \
    echo 'Running pydocstyle' && \
    pydocstyle . && \
    echo 'Running Bandit' && \
    bandit --recursive ./ --configfile .bandit.yml

# Run unit tests only during build time to provide a fast fail mode if
# something is broken, as well as making it impossible for someone to sneak in
# a "unit" test which has external dependencies.
RUN pytest --cov nornir_batfish --color yes -vvv tests

# Run full test suite including integration
ENTRYPOINT ["pytest"]

# Default to running colorful, verbose pytests
CMD ["--cov=nornir-batfish", "--color=yes", "-vvv"]
