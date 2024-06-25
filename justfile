# list recipes
default:
  just --list

# run in auto headless mode, supports arguments
auto *FLAGS:
    python -m gv_auto {{FLAGS}}

# run in auto mode, without sleep, headed browser
autoview:
    python -m gv_auto --no-sleep --no-headless

# get statistics on bricks
stats:
    (cd stats; python parse_bricks_from_log.py; python calc_statistics.py)

# run in manual mode
man:
    python -m gv_auto --manual

# Variables
DOCKER_USER := "pyrogn"
IMAGE_NAME := "seleniumbase"
TAG := "latest"
DOCKERFILE_PATH := "."
DOCKER_IMAGE := DOCKER_USER + "/" + IMAGE_NAME + ":" + TAG
CONTAINER_NAME := "seleniumbase_app"
HOST_DIR := "$(pwd)"
CONTAINER_DIR := "/app"

# Build image
build:
    docker build -t {{DOCKER_IMAGE}} {{DOCKERFILE_PATH}}

# Run bot with headed UC mode with virtual monitor in Linux
autostealth: build
    docker run --platform linux/amd64 -it {{DOCKER_IMAGE}} --name {{CONTAINER_NAME}} -v {{HOST_DIR}}:{{CONTAINER_DIR}} python -m gv_auto --extra-stealth

# Clean image
clean:
    docker rmi {{DOCKER_IMAGE}}

# Stop and remove the Docker container
stop:
    docker stop {{CONTAINER_NAME}}
    docker rm {{CONTAINER_NAME}}


