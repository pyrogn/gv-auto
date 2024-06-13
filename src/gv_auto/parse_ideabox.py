from bs4 import BeautifulSoup
import pandas as pd

# Load the HTML file
with open("/mnt/data/ideabox.html", "r", encoding="utf-8") as file:
    content = file.read()

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(content, "html.parser")

# Find all voting links under "Голосование:" but not under "Вклад:"
voting_links_section = soup.find_all("div", class_="v_link_capt")
vote_links = []

for section in voting_links_section:
    if section.text.strip() == "Голосование:":
        next_sibling = section.find_next_sibling("div")
        vote_links = next_sibling.find_all("a")
        break

# Extract the relevant links
vote_links = [f"https://godville.net{a['href']}" for a in vote_links]

# Prepare the table to store the data
data = []

# Iterate through each voting link to extract information
for link in vote_links:
    category = link.split("/")[-1]

    # Simulate opening and parsing each link (in a real scenario, you would fetch the content of each link)
    rows = soup.find_all("div", class_="vote_row")

    for row in rows:
        main_text = row.find("div", class_="text").contents[1].strip()
        sub_text = (
            row.find("div", class_="cmnt_c").text.strip()
            if row.find("div", class_="cmnt_c")
            else ""
        )

        vote_yes = int(row.find("div", class_="vote-counts-up").text.strip())
        vote_no = int(row.find("div", class_="vote-counts-down").text.strip())

        vote_dupe_text = row.find("div", class_="vote-counts-dupe").text.strip()
        vote_dupe = int(vote_dupe_text) if vote_dupe_text else 0

        data.append([category, main_text, sub_text, vote_yes, vote_no, vote_dupe])

    # Stop collecting data after "Контент из игры"
    if row.find(id="er_header") and row.find(id="er_header").text == "Контент из игры":
        break

# Convert the data into a pandas DataFrame
df = pd.DataFrame(
    data,
    columns=["Category", "Main Text", "Sub Text", "Vote Yes", "Vote No", "Vote Dupe"],
)
