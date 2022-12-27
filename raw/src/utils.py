import time
import pathlib
import datetime
import json
import os
import shutil
import urllib.request

import cv2


def scroll_down(driver):
    """
    A function for scrolling the page using selenium webdriver
    """

    # Get scroll height.
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:

        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load the page.
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height



def download_image(img_url, image_path):
    """
    Downloads an image into dir_name, given its url.
    :param url: (str) image url
    :param dir_name: (str) client name
    :param store: (str) App Store or GooglePlay
    :return: None
    """
    dirs_in_path = image_path.split("/")[:-1]
    dir_name = "/".join(dirs_in_path)

    pathlib.Path(f'{dir_name}').mkdir(
        parents=True,
        exist_ok=True
    )
    img_name = img_url.replace('/', '-')
    if img_name.endswith('.png'):
        urllib.request.urlretrieve(img_url, image_path)
    else:
        urllib.request.urlretrieve(img_url, image_path)


    # with open(f"{download_images_dir}/{url.replace('/', ' ')}.png", 'wb') as handle:
    #     response = requests.get(url, stream=True)
    #
    #     if not response.ok:
    #         print(response)
    #
    #     for block in response.iter_content(1024):
    #         if not block:
    #             break
    #
    #         handle.write(block)


def save_query_results(results_dict, file_path, store):
    """
    Saves app info scraped from store.
    :param results_dict: (dict) dict of app properties to save
    :param dir_name: (str) client name
    :param store: (str) App Store or GooglePlay
    :return: None

    """
    dirs_in_path = file_path.split("/")[:-1]
    dir_name = "/".join(dirs_in_path)

    pathlib.Path(dir_name).mkdir(
        parents=True,
        exist_ok=True
    )

    with open(file_path, 'w') as h:
        json.dump(results_dict, h)


def create_anchor_dirs():
    with open('files/clients.json', 'r') as handle:
        clients = json.load(handle)

    stores = os.listdir('data/scrap/')

    for client in clients.keys():
        for store in stores:
            pathlib.Path(f'data/anchors/{client}/{store}/').mkdir(
                parents=True,
                exist_ok=True
            )


def create_train_ds(client, store, save):
    if save:
        save_dir = f'data/anchors/{client}/{store}/'
        create_anchor_dirs()

    qdir = f'data/scrap/{store}/{client}/images'

    ds = {}

    for ii, imname in enumerate(os.listdir(qdir)):
        qimg = cv2.imread(f'{qdir}/{imname}')

        cv2.imshow('query image', qimg)
        k = cv2.waitKey(0) & 0xFF
        if k == ord('s'):
            owned = True
            print(f'client: {client}')
        else:
            owned = False
            print(f'client: other')

        cv2.destroyWindow('query image')

        ds[f'{imname}'] = owned

        if save and owned:
            cv2.imwrite(f'{save_dir}/{client}_anchor_{ii}.png', qimg)

    pathlib.Path(f'data/misc/{client}/').mkdir(parents=True, exist_ok=True)
    with open(f'data/misc/{client}/{store}_train_ds.json', 'w') as handle:
        json.dump(ds, handle)

    return ds


def delete_client_img_dir(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
