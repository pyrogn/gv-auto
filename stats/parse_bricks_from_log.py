import re
import numpy as np
import pandas as pd


def parse_logs(file_path):
    log_pattern = re.compile(
        r"(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2},\d{3} - INFO - .*\|bricks:(\d+)\|.*"
    )

    log_data = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            match = log_pattern.match(line)
            if match:
                date = match.group(1)
                bricks = int(match.group(2))
                log_data.append((date, bricks))

    return log_data


def get_latest_bricks_per_day(log_data):
    df = pd.DataFrame(log_data, columns=["date", "bricks"])
    df = df.groupby("date").last().reset_index()
    df["day"] = np.arange(1, len(df) + 1)

    return df[["day", "bricks"]]


file_path = "../bot.log"

log_data = parse_logs(file_path)

bricks_df = get_latest_bricks_per_day(log_data)

bricks_df.to_csv("brick_stats.csv", index=False)
