import argparse
import os
from src import utils
from src import scrap_appstore
from src import scrap_googlePlay


def main(CLIENT, STORE, download_images_dir, download_results_file):
    if STORE == 'googlePlay':
        try:
            utils.delete_client_img_dir(f'data/scrap/googlePlay/{CLIENT}')
        except FileNotFoundError:
            pass
        scrap_googlePlay.main(CLIENT, download_images_dir, download_results_file)

    elif STORE == 'appstore':
        try:
            utils.delete_client_img_dir(f'data/scrap/appstore/{CLIENT}')
        except FileNotFoundError:
            pass
        scrap_appstore.main(CLIENT, download_images_dir, download_results_file)


if __name__ == '__main__':
    args_help = {
        'client': f"one of the following strings: {list(os.listdir('data/anchors/'))}",
    }
    parser = argparse.ArgumentParser()
    parser.add_argument('client', help=args_help['client'])
    args = parser.parse_args()

    CLIENT = args.client

    main(CLIENT)
