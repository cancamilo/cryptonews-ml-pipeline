# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install netcat
RUN apt-get update && apt-get install -y netcat-openbsd

# Upgrade pip and install Poetry
RUN python3 -m pip install --upgrade pip && pip3 install poetry

# Copy only the pyproject.toml and poetry.lock (if exists) to use Docker cache
COPY pyproject.toml poetry.lock* /usr/src/app/

# Install project dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-dev --no-cache && \
    poetry cache clear pypi --all

RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir sentence-transformers

# Copy the rest of the application
COPY . /usr/src/app
COPY .env.docker .env
COPY wait-mq.sh /wait-mq.sh
RUN chmod +x /wait-mq.sh

# Make port 8000 available to the world outside this container
EXPOSE 8000

ENV RUST_BACKTRACE=1

CMD ["/wait-mq.sh","python", "-m", "bytewax.run", "data_flow/bytewax_pipeline"]