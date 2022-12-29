import re
import requests
from bs4 import BeautifulSoup
from raw.src.utils import download_image, save_query_results


DOWNLOAD_IMAGES = True
SAVE_RESULTS = True
STORE = 'appstore'



def get_app_urls(url):
    """
    Given a search query url, get urls from apps and it logos.
    :param url: (str)
    :return app_urls: (list) apps url list
    :return img_urls: (list) app images url list
    """
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')


    app_view_more_list = soup.find_all(class_='icon icon-after icon-chevronright')
    app_img_list = soup.find_all(class_='rf-serp-explore-image')

    img_urls = []
    app_urls = []
    for app_view_more, app_img in zip(app_view_more_list, app_img_list):
        app_url = app_view_more['href']
        app_urls.append(app_url)

        app_img_url = app_img['src']
        app_img_url = app_img_url.replace('350', '256')
        img_urls.append(app_img_url)

    return app_urls, img_urls


def get_app_data(app_url, img_url):
    """
    Gets app data from store.
    :param app_url: (str) store app url
    :param img_url: (str) image url
    :return app_data: (dict) dictionary with app features.
    """
    response = requests.get(app_url)
    html = response.content
    driver = BeautifulSoup(html, 'html.parser')


    app_name_el = driver.find(class_='product-header__title app-header__title')
    if app_name_el is None:
        return None
    app_name_text = app_name_el.text
    app_name_split = re.split(r'(\d+)', app_name_text)
    app_name = ''.join(app_name_split[:-2])[:-1]
    app_name = app_name.replace("\n", "")

    developer_el_parent = driver.find(class_='product-header__identity app-header__identity')
    developer_el = developer_el_parent.find(class_='link')
    developer = developer_el.text.replace("\n", "")

    app_data = {
        'search_query': app_url,
        'app_name': app_name,
        'developer': developer,
        'img_url': img_url,
        'app_url': app_url
    }

    return app_data


def main(search_query_0, download_images_dir, download_results_file):
    search_query = search_query_0.replace(' ', '-')
    url = f'https://www.apple.com/us/search/{search_query}?src=globalnav'
    app_urls, img_urls = get_app_urls(url)

    apps_data = []

    for app_url, img_url in zip(app_urls, img_urls):

        if img_url == '':
            continue
        app_data = get_app_data(app_url, img_url)
        if app_data is None:
            continue
        app_name = app_data['app_name']
        if DOWNLOAD_IMAGES:
            image_path = f'{download_images_dir}/{app_name}.png'
            download_image(img_url, image_path)
            # download_image(img_url, download_images_dir)
        else:
            image_path = None

        app_data['img_path'] = image_path
        apps_data.append(app_data)

    if SAVE_RESULTS:
        save_query_results(apps_data, download_results_file, STORE)


if __name__ == '__main__':
    main()
