# list recipes
default:
  just --list

# run in auto headless mode, supports arguments
auto *FLAGS:
    python -m gv_auto {{FLAGS}}

# run in auto mode, without sleep, headed browser
autoview:
    python -m gv_auto --no-sleep --no-headless

# run in manual mode
man:
    python -m gv_auto --manual
