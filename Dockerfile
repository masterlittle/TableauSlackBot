FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV PYTHONPATH "${PYTHONPATH}:/"
ENV PORT=8000
ENV ENV=production

RUN apt-get -y update
RUN apt-get install -yqq unzip curl
RUN apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libnss3 lsb-release xdg-utils


# Install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

# set display port to avoid crash
ENV DISPLAY=":20"

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy using poetry.lock* in case it doesn't exist yet

COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry install --no-root --no-dev

COPY ./.env /app/

COPY ./app /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--reload", "--host", "::"]