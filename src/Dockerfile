# syntax=docker/dockerfile:1

FROM python:3.10.0-slim-bullseye

# Prevents Python from writing pyc files to disc (equivalent to "python -B" option).
ENV PYTHONDONTWRITEBYTECODE=1

# Prevents Python from buffering stdout and stderr (equivalent to "python -u" option).
ENV PYTHONUNBUFFERED=1

# Skips the auto-update of built-in blacklist on startup.
# Blacklist is already downloaded during module installation.
ENV PY3VE_IGNORE_UPDATER=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Поправить путь
COPY ./src .

CMD [ "python3", "-m" , "app"]

