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
IMAGE_NAME := "gv-auto"
TAG := "latest"
DOCKERFILE_PATH := "."
DOCKER_IMAGE := IMAGE_NAME + ":" + TAG
CONTAINER_NAME := "seleniumbase_app"
HOST_DIR := "$(pwd)"
CONTAINER_DIR := "/app"

# Build image
build:
    docker build --platform linux/amd64 -t {{DOCKER_IMAGE}} {{DOCKERFILE_PATH}}

# Run bot with headed UC mode with virtual monitor in Linux
autostealth: build
    docker run --rm --platform linux/amd64 --name {{CONTAINER_NAME}} -v {{HOST_DIR}}:{{CONTAINER_DIR}} -w {{CONTAINER_DIR}} -it {{DOCKER_IMAGE}} python3 -m gv_auto --extra-stealth

# Run seleniumbase headed in Linux
stealth *FLAGS: build
    docker run --rm --platform linux/amd64 --name {{CONTAINER_NAME}} -v {{HOST_DIR}}:{{CONTAINER_DIR}} -w {{CONTAINER_DIR}} -it {{DOCKER_IMAGE}} {{FLAGS}}
