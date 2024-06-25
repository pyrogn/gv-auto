# Use the previously built image as the base
FROM pyrogn/seleniumbase:latest

# Set the working directory inside the container
WORKDIR /app

COPY pyproject.toml requirements.lock requirements-dev.lock ./
COPY ./src ./src

RUN pip install rye
RUN rye sync

# COPY . .

# Specify the entrypoint command
# ENTRYPOINT ["python", "your_script.py"]
