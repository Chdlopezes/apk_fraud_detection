from bs4 import BeautifulSoup
import requests
from src.utils import download_image, save_query_results


DOWNLOAD_IMAGES = True
SAVE_RESULTS = True
STORE = 'googlePlay'


def get_principal_app_data(soup, url, download_images_dir):
    principal_app_url = soup.find(class_='Qfxief')['href']

    principal_app_box = soup.find(class_='y4nHb')

    principal_name_el = principal_app_box.find(class_='vWM94c')
    principal_app_name = principal_name_el.text

    principal_developer_el = principal_app_box.find(class_='LbQbAe')
    principal_developer = principal_developer_el.text

    principal_img_el = principal_app_box.find(class_='T75of KvQfUd')
    principal_img_url = principal_img_el['src'].replace('s52', 's256')

    if DOWNLOAD_IMAGES:
        download_image(principal_img_url, download_images_dir)

    principal_app_data = {
        'search_query': url,
        'app_name': principal_app_name,
        'developer': principal_developer,
        'img_url': principal_img_url,
        'app_url': principal_app_url
    }

    return principal_app_data


def main(search_query_0, download_images_dir, download_results_file):
    search_query = search_query_0.replace(' ', '%20')
    url = f'https://play.google.com/store/search?q={search_query}&c=apps'
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')

    try:
        principal_app_data = get_principal_app_data(soup, url, download_images_dir)
        apps_data = [principal_app_data]
    except:
        apps_data = []

    class_root = soup.find_all(class_='Si6A0c Gy4nib')
    for i, element in enumerate(class_root, start=1):
        name_el = element.find(class_='DdYX5')
        app_name = name_el.text

        developer_el = element.find(class_='wMUdtb')
        developer = developer_el.text

        img_el = element.find(class_='T75of stzEZd')
        img_url = img_el['src']
        img_url = img_url.replace('s64', 's256')

        if DOWNLOAD_IMAGES:
            image_path = f'{download_images_dir}/{app_name}.png'
            download_image(img_url, image_path)
        else:
            image_path = None

        app_url = element['href']

        app_data = {
            'search_query': url,
            'app_name': app_name,
            'developer': developer,
            'img_url': img_url,
            'img_path': image_path,
            'app_url': app_url
        }

        apps_data.append(app_data)

    if SAVE_RESULTS:
        save_query_results(apps_data, download_results_file, STORE)



if __name__ == '__main__':
    main()
