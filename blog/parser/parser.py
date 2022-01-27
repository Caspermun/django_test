import csv

import requests
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent

# from blog.models import Ad

URL = 'https://www.house.kg'
PAGE = '/kupit?page='
USER_AGENT = UserAgent(verify_ssl=False)


def get_html(url, page=None):
    page = PAGE + str(page)
    get_from_page = url + page
    r = requests.get(get_from_page, headers={'User-Agent': USER_AGENT.random})
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
    url_list = []
    with open(file, 'r', encoding='utf-8') as f:
        for i in csv.reader(f):
            if i:
                url = i[0]
                if not url in url_list:
                    url_list.append(url)
    return url_list


def get_detail_html(urls):
    for url in urls:
        get_from_page = URL + url
        html = requests.get(get_from_page, headers={'User-Agent': USER_AGENT.random}).text
        soup = BS(html, 'html.parser')
        try:
            elements = soup.find('div', class_='details-stat-block').find('span', class_='dollars')
            if elements and len(elements) > 0:
                print(elements.text)
        except:
            continue


if __name__ == '__main__':
    # for i in range(1, 11):
    #     html = get_html(URL, page=i)
    #     get_data_from_html(html)
    #     print(f'Страница {i} успешно спарсена')
    # read_csv('10_pages.csv')
    get_detail_html(read_csv('10_pages.csv'))
