# Use the previously built image as the base
FROM pyrogn/seleniumbase:latest

# Set the working directory inside the container
WORKDIR /app

COPY pyproject.toml requirements.lock requirements-dev.lock README.md ./
COPY ./src ./src

RUN pip install uv
RUN uv pip install --system -r requirements-dev.lock

# Specify the entrypoint command
CMD ["/bin/bash"]
