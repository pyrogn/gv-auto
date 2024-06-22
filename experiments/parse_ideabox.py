import os
from bs4 import BeautifulSoup
import pandas as pd


def parse_vote_row(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    soup = BeautifulSoup(content, "html.parser")

    # Extract all hrefs in id="votes_links" with class="v_link_val"
    votes_links_div = soup.find("div", id="votes_links")
    vote_links = votes_links_div.find_all("div", class_="v_link_val")

    # Extract and print the hrefs
    hrefs = [a["href"].split("/")[-1] for div in vote_links for a in div.find_all("a")]
    print(hrefs)

    # Prepare the table to store the data
    data = []

    # Iterate through each vote_row to extract information
    rows = soup.find_all("div", class_="vote_row")

    for row in rows:
        try:
            text_div = row.find("div", class_="text").div.div
        except AttributeError:
            continue

        title = ""
        main_text = ""
        sub_text = ""

        # Check if there is a title
        title_div = text_div.find("div", class_="fch_style")
        if title_div:
            title = title_div.text.strip()

        # Extract the main text
        main_text_elements = text_div.contents
        for element in main_text_elements:
            if isinstance(element, str):
                main_text += element.strip()
            elif element.name == "div" and "fch_style" not in element.get("class", []):
                sub_text = element.text.strip()

        sub_text = (
            row.find("div", class_="cmnt_c").text.strip()
            if row.find("div", class_="cmnt_c")
            else sub_text
        )

        def parse_votes(class_):
            try:
                if class_ == "vote-counts-dupe":
                    print(row.find("div", class_=class_).text)
                vote = int(row.find("div", class_=class_).text.strip())
            except AttributeError:
                vote = 0
            return vote

        vote_yes = parse_votes("vote-counts-up")
        vote_no = parse_votes("vote-counts-down")
        # vote_dupe = parse_votes("vote-counts-dupe")

        data.append(
            [
                file_path.split("/")[-1].split(".")[0],
                title,
                main_text,
                sub_text,
                vote_yes,
                vote_no,
                # vote_dupe,
            ]
        )

    return data


def main():
    directory = "pages/ideabox/"
    all_data = []

    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            file_path = os.path.join(directory, filename)
            file_data = parse_vote_row(file_path)
            all_data.extend(file_data)

    # Convert the data into a pandas DataFrame
    df = pd.DataFrame(
        all_data,
        columns=[
            "category",
            "title",
            "main_text",
            "sub_text",
            "yes",
            "no",
            # "Vote Dupe",
        ],
    )
    df = df[~((df["yes"] == 0) & (df["no"] == 0))]
    df["agreement"] = (df["yes"] / (df.yes + df.no)).round(3)
    df.to_csv("parsed_votes.csv", index=False)
    print(df)


if __name__ == "__main__":
    main()
