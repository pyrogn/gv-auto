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
