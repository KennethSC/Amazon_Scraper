from pathlib import Path
from selenium import webdriver
from bs4 import BeautifulSoup
import csv
import os

DRIVER_PATH = str(Path('chromedriver').resolve())
BROWSER = webdriver.Chrome(executable_path=DRIVER_PATH)

def get_html(url):
    BROWSER.get(url)
    html = BROWSER.page_source

    return html


def scrape_data(card):

    try:
        h2 = card.h2
    except:
        title = ''
        url = ''
    else:
        title = h2.text.strip()
        url = h2.a.get('href')

    try:
        price = card.find('span', class_='a-price-whole').text.strip('.').strip()
    except:
        price = ''
    else:
        price = price.replace(',', '')

    if url != '':
        url = 'https://www.amazon.com/' + url

    if price != '':
        price = '$' + price

    data = {
        'title' : title,
        'url' : url,
        'price' : price,
    }

    return data


# Writes to a created csv file each product's
# name, price, # of reviews, # sold, and link
# with each product's info being in one row.
def write_csv(file, prod_lst):
    with open(file, 'a') as f:
        fields = ['title', 'price', 'url']
        writer = csv.DictWriter(f, fieldnames = fields)

        for prod in prod_lst:
            writer.writerow(prod)


# Creates a csv file and stores it in the users 
# 'Documents' folder, also handles duplicate file names.
def make_csv(query):

    query = query.replace('+', '_')

    file_in_Docs = os.path.join(os.path.expanduser('~'), 'Documents', str(query) + '.csv')

    file_ctr = 1
    while os.path.isfile(file_in_Docs):
        new_name = f'{query}({file_ctr}).csv'
        file_in_Docs = os.path.join(os.path.expanduser('~'), 'Documents', str(new_name))
        file_ctr+=1

    return file_in_Docs



def main():

    prod = input('Type the name of the product and press ENTER: ').replace(' ', '+').strip()
    csv_file = make_csv(prod)
    prod_data = []

    for page in range(1, 5):
        url = f'https://www.amazon.com/s?k={prod}&page={page}' 
               
        html = get_html(url)
        soup = BeautifulSoup(html, 'lxml')
        cards = soup.find_all('div', {'data-asin' : True, 'data-component-type' : 's-search-result'})
        
        for card in cards:
            data = scrape_data(card)
            title = data['title']
            if not any(d['title'] ==  title for d in prod_data):
                prod_data.append(data)

        write_csv(csv_file, prod_data)

    print('Done')


if __name__ == '__main__':
    main()


