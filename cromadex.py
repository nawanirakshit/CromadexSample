import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
from openpyxl import Workbook


def print_table():
    my_list = []
    c.execute("SELECT * FROM cromadex_products")  # Replace with your desired table and columns
    results = c.fetchall()
    for row in results:
        my_list.append(row)
        print(row)


def check_site(start_url, page_no, end_url):
    final_url = start_url + str(page_no) + end_url
    print("Final URL = " + final_url)
    response = requests.get(final_url)

    # Check for successful response
    if response.status_code == 200:

        soup = BeautifulSoup(response.content, "html.parser")
        parent_div = soup.find("div", "facets-facet-browse-items")

        direct_child_divs = parent_div.find_all("div", recursive=False)
        for child_div in direct_child_divs:
            all_a = child_div.find_next("div", "facets-item-cell-list")
            sku = all_a["data-sku"]
            href = all_a.find("a", "facets-item-cell-list-anchor")["href"]
            src = all_a.find("img")["src"]
            name = all_a.find("span", itemprop="name").text

            insert_query = """
            INSERT INTO cromadex_products (sku, name,href,src) VALUES (?, ?, ?, ?)
            """
            values = (sku, name, href, src)  # Replace values as needed
            c.execute(insert_query, values)
            conn.commit()

            dynamic_data = [sku, name, name, src]
            print(dynamic_data)
            sheet.append(dynamic_data)

        if page_no < 10:
            page_no = page_no + 1
            check_site(start_url, page_no, end_url)
        else:
            print_table()
            conn.close()
            wb.save('my_data.xlsx')
            # Save the DataFrame to an Excel file

    else:
        print_table()
        conn.close()
        print("Error fetching URL:", response.status_code)


string1 = "https://standards.chromadex.com/all-products?page="
pageNo = 1
string2 = "&show=48"
url = string1 + str(pageNo) + string2  # Output: Hello 25!

conn = sqlite3.connect('croma_dex.db')
c = conn.cursor()

c.execute(f"DROP TABLE IF EXISTS cromadex_products")
# Create a table named "users"
c.execute("""CREATE TABLE IF NOT EXISTS cromadex_products(
             id INTEGER PRIMARY KEY AUTOINCREMENT
             ,sku TEXT
             ,name TEXT
             , href TEXT
             , src TEXT)""")

data = ['SKU', 'Name', 'href', 'src']

wb = Workbook()
sheet = wb.active

# Write data cell by cell or use DataFrame-like methods
# sheet.cell(row=1, column=1)
sheet.append(data)

wb.save('my_data.xlsx')

check_site("https://standards.chromadex.com/all-products?page=", 1, "&show=48")
