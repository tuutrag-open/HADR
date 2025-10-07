# ================================================================
# path: tuutrag/scrapers.py
# brief: tuutrag module exports
# ================================================================
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


chrome_options = Options()
chrome_options.add_argument("--headless=new")


driver = webdriver.Chrome(options=chrome_options)


# MAGENTA BOOKS
driver.get("https://ccsds.org/publications/magentabooks/")


html = driver.page_source
soup = BeautifulSoup(html, "html.parser")


# Retrieve and filter all links within table data elements
links = [row.find("a")["href"] for row in soup.select("td:has(a)")]
links = [link for link in links if "gravity_forms" in link]
links = list(dict.fromkeys(links))


magenta = []
for i in range(40):
    book = []

    # Retrieves table data for each book
    # and adds links to metadata
    rows = soup.select(f'td[data-row-index="{i}"]')
    link = links[i]
    book.append(link)

    # Adds metadata to list and matches pdf name to
    # name in data folder
    row_counter = 1
    for row in rows:

        row = row.get_text(strip=True)

        if row_counter == 3:
            row = row.replace(" ", "_").replace(".", "_")
            row = row + ".pdf"

        book.append(row)
        row_counter += 1

    # Removes empty elements in metadata
    book = list(filter(None, book))

    # Adds each book(metadata) to a list of magenta books
    magenta.append(book)


# BLUE BOOKS
driver.get("https://ccsds.org/publications/bluebooks/")


html = driver.page_source
soup = BeautifulSoup(html, "html.parser")


# Retrieve and filter all links within table data elements
links = [row.find("a")["href"] for row in soup.select("td:has(a)")]
links = [link for link in links if "gravity_forms" in link]
links = list(dict.fromkeys(links))


blue = []
for i in range(99):
    book = []

    rows = soup.select(f'td[data-row-index="{i}"]')
    link = links[i]
    book.append(link)

    row_counter = 1
    for row in rows:
        if row_counter > 10:
            break

        row = row.get_text(strip=True)
        if row_counter == 3:
            row = row.replace(" ", "_").replace(".", "_")
            row = row + ".pdf"

        book.append(row)
        row_counter += 1

    book = list(filter(None, book))

    # Adds each book(metadata) to a list of blue books
    blue.append(book)


headers = [
    "Link:",
    "PDF Name:",
    "Title:",
    "Book Type:",
    "Issue Number:",
    "Published Date:",
    "Description:",
    "Working Group:",
    "ISO Equivalent:",
]


# Adds list of books to dictionary to
# store in a JSON file
Magenta_meta = []
for idx, book in enumerate(magenta):
    book_dict = {}
    for i, data in enumerate(book):

        book_dict[headers[i]] = data
    if len(book) == 8:
        book_dict[headers[-1]] = ""

    Magenta_meta.append(book_dict)


blue_meta = []
for idx, book in enumerate(blue):
    book_dict = {}
    for i, data in enumerate(book):

        book_dict[headers[i]] = data
    if len(book) == 8:
        book_dict[headers[-1]] = ""

    blue_meta.append(book_dict)


with open("../data/meta/magentabook_meta.json", "w", encoding="utf-8") as file:
    json.dump(Magenta_meta, file, indent=4)


with open("../data/meta/bluebook_meta.json", "w", encoding="utf-8") as file:
    json.dump(blue_meta, file, indent=4)
