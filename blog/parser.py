import csv

import requests
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent

from blog.models import Ad

URL = 'https://www.house.kg'
PAGE = '/kupit?page='


def get_html(url, page=None):
    page = PAGE + str(page)
    get_from_page = url + page
    ua = UserAgent(verify_ssl=False)
    r = requests.get(get_from_page, headers={'User-Agent': ua.random})
    return r.text


def get_data_from_html(html):
    soup = BS(html, 'html.parser')
    ads = soup.find('div', class_='listings-wrapper').find_all('div', class_='listing')
    ads_list = []
    for j in ads:
        title_tag = j.find('p', class_='title')
        detail_url = title_tag.find('a').get('href')
        title = title_tag.text.strip()
        price = j.find('div', class_='price').text
        description = j.find('div', class_='description').text.strip()
        image = j.find('img', class_='temp-auto')
        try:
            image = image.get('data-src')
        except:
            pass
        ads_list.append(dict(detail_url=detail_url, title=title, price=price, description=description, image=image))

    with open('10_pages.csv', 'a', encoding='utf-8') as f:
        for h in ads_list:
            writer = csv.writer(f)
            writer.writerow([v for k, v in h.items()])


def read_csv(file):
    with open(file, 'r', encoding='utf-8') as f:
        for i in csv.reader(f):
            if i:
                title = i[1]
                price = i[2]
                desc = i[3]
                image = i[4]
                Ad.objects.create(title=title)
                Ad.objects.create(price=price)
                Ad.objects.create(description=desc)
                Ad.objects.create(image=image)



if __name__ == '__main__':
    # for i in range(1, 11):
    #     html = get_html(URL, page=i)
    #     get_data_from_html(html)
    #     print(f'Страница {i} успешно спарсена')
    read_csv('10_pages.csv')