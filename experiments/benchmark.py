from pathlib import Path
from seleniumbase import SB
from bs4 import BeautifulSoup
import time


def get_uri_for_html(path: str) -> str:
    return (Path.cwd() / path).as_uri()


def benchmark_seleniumbase(selector: str, uri: str, iterations: int = 100) -> float:
    total_time = 0
    with SB(uc=True, headless2=True) as sb:
        for _ in range(iterations):
            sb.uc_open(uri)
            start_time = time.time()
            element_text = sb.get_text(selector)
            assert element_text == "жалкие 83 монеты"
            total_time += time.time() - start_time
    return total_time / iterations


def benchmark_html_find(selector: str, uri: str, iterations: int = 100) -> float:
    total_time = 0
    with SB(uc=True, headless2=True) as sb:
        for _ in range(iterations):
            sb.uc_open(uri)
            start_time = time.time()
            html = sb.get_page_source()
            # Assume some method to find text from html
            soup = BeautifulSoup(html, "html.parser")
            element = soup.select_one(selector)
            if element:
                element_text = element.get_text()
                assert element_text == "жалкие 83 монеты"
            total_time += time.time() - start_time
    return total_time / iterations


def benchmark_bs4(selector: str, uri: str, iterations: int = 100) -> float:
    total_time = 0
    with SB(uc=True, headless2=True) as sb:
        sb.uc_open(uri)
        html = sb.get_page_source()
    soup = BeautifulSoup(html, "html.parser")
    for _ in range(iterations):
        start_time = time.time()
        element = soup.select_one(selector)
        if element:
            element_text = element.get_text()
            assert element_text == "жалкие 83 монеты"
        total_time += time.time() - start_time
    return total_time / iterations


html_uri = get_uri_for_html("pages/no_response_true.mhtml")
selector = "#hk_gold_we > div.l_val"

avg_time_seleniumbase = benchmark_seleniumbase(selector, html_uri)
avg_time_html_find = benchmark_html_find(selector, html_uri)
avg_time_bs4 = benchmark_bs4(selector, html_uri)

print(f"Average time using seleniumbase method: {avg_time_seleniumbase:.6f} seconds")
print(
    f"Average time getting page and finding element: {avg_time_html_find:.6f} seconds"
)
print(f"Average time parsing text using bs4: {avg_time_bs4:.6f} seconds")
