from pathlib import Path


def get_uri_for_html(path: str) -> str:
    return (Path.cwd() / path).as_uri()
