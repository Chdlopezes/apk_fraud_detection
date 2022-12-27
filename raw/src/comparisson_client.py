import json
import datetime
import pathlib
import pandas as pd
from raw.src import scrap_stores
from raw.src.study_processors_modules import create_study, process_study
from raw.src.study_processors_modules import agg_study, collapse_agg


class ComparisonClient:

    def __init__(self, client, store, save_study=True):
        """
        Constructor for ComparisonClient class. Must be specified the client name, the web mobile application store.
        Optional parameter is save_study to specify if all metrics are stored in 'data/misc/{client}/' dir
        as a json file.
        @param client: (str) Name of the client. A list of possible clients is at: files/clients.csv
        @param store: (str) Name of the store to perform the images comparison w.r.t the client anchor(s).
            possible values: 'googlePlay' or 'appstore'.
        @param save_study: (bool) If True (default) all the metrics are stored in a json file located at
        'data/misc/{client}/' where {client} is the name of client specified at param:client.
        """
        self.client = client
        self.store = store
        self.anchors_path = f'data/anchors/{client}/{store}'
        self.clients_info_path = 'files/clients.json'
        self.save_study = save_study
        self.qi_dict = {'name': None,
                        'developer': 'Unknown',
                        }

    def set_anchors_path(self, anchors_path):
        """
        Method to change the default anchors path, provide new path in the parameter anchors_path
        @param anchors_path: "str": path where the client anchors logos are located.
        """

        self.anchors_path = anchors_path

    def set_clients_info_path(self, clients_info_path):
        self.clients_info_path = clients_info_path

    def set_query_image_developer(self, developer):
        self.qi_dict["developer"] = developer

    @classmethod
    def save_scrap_info_from_client(cls, client, store, download_images_dir, download_results_file):
        """
        Use this function to compute a web scrapping in the mobile application web store defined in "store" for the
        client set at "client". All logos found for this query are located in the dir path: "download_images_dir"

        @param client:  (str) Name of the client
        @param store: (str) name of the app store to search in: 'googlePlay' or 'appstore'
        @param download_images_dir: (str) path where logo images are going to be stored.
        """
        scrap_stores.main(CLIENT=client,
                          STORE=store,
                          download_images_dir=download_images_dir,
                          download_results_file=download_results_file)

    @classmethod
    def load_scrap_info_from_client(cls, scrap_info_path):
        with open(scrap_info_path, "r") as h:
            scrap_info_json = json.load(h)
        return scrap_info_json

    def compare_anchors_with_query(self, query_info):
        """
        This method computes the comparisson between a user defined image (query_img_path) pretending to be from a given
        client and all anchors from that client located in anchors dir.
        @param query_img_path: (str) image_path of the image intended to compare with all anchors
        @return: (Dict) Dictionary containing all the metrics computed for the comparison between query_img and anchors
        """

        query_img_path = query_info['img_path']
        self.qi_dict['name'] = query_img_path.split("/")[-1]
        study = create_study(anchors_path=self.anchors_path,
                             query_img_path=query_img_path,
                             query_img_name=self.qi_dict['name'])
        if isinstance(study, list):
            if not study:
                return None
        if isinstance(study, pd.DataFrame):
            if study.empty:
                return None

        study = process_study(study, 'list')
        if self.save_study:
            save_dir = f'data/misc/{self.client}'
            pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
            with open(f'{save_dir}/{self.store}_study.json', 'w') as handle:
                json.dump(study, handle)

        with open(self.clients_info_path, 'r') as handle:
            client_info = json.load(handle)

        agg = agg_study(study)
        collapsed_agg = collapse_agg(agg)

        self.qi_dict['developer'] = query_info['developer']
        if self.qi_dict['developer'] in client_info[self.client]['developer'][self.store]:
            self.qi_dict['valid'] = True
        else:
            self.qi_dict['valid'] = False

        score_item = collapsed_agg[collapsed_agg['name'] == self.qi_dict['name']].score
        if score_item.empty:
            print("There's no score found")
        else:
            score = float(score_item)
            self.qi_dict['score'] = score

        return self.qi_dict

    def save_matches_results(self, qi_dict, save_dir=None):
        """
        Use this method to store the dictionary containing the metrics obtained for the comparison of each image in the
        scrap search with respect to the anchors in the dir 'reports/{store}/{client}/' as a csv file
        @param qi_dict: dictionary with the metrics obtained using the method: compare_anchors_with_query
        @param save_dir: save dir if a different path that 'reports/{store}/{client}/' is desired
        """
        results_df = pd.DataFrame(qi_dict, index=[0])
        if save_dir is None:
            save_dir = f'reports/{self.store}/{self.client}'

        pathlib.Path(save_dir).mkdir(
            parents=True,
            exist_ok=True
        )
        matches_filename = qi_dict['name'].replace('.png', '')
        results_df.to_csv(f'{save_dir}/{matches_filename}.csv', index=False)


if __name__ == '__main__':
    print("*"*50 + "\n" + "Start")
    with open("client_query.json", "r") as file_h:
        client_query = json.load(file_h)

    CLIENT = client_query["client"]
    STORE = client_query["store"]

    DATE = str(datetime.datetime.now().date())
    DIR_OF_QUERIES_IMGS = f'data/scrap/{STORE}/{CLIENT}/images/{DATE}'
    PATH_SCRAP_INFO_JSON = f'data/scrap/{STORE}/{CLIENT}/query_results/{DATE}.json'

    compare_obj = ComparisonClient(client=CLIENT, store=STORE)
    compare_obj.save_scrap_info_from_client(client=CLIENT,
                                            store=STORE,
                                            download_images_dir=DIR_OF_QUERIES_IMGS,
                                            download_results_file=PATH_SCRAP_INFO_JSON)
    all_results = []
    full_results = []
    # open json with query info and load the corresponding image using it
    scrap_info_json = compare_obj.load_scrap_info_from_client(PATH_SCRAP_INFO_JSON)
    for query_info in scrap_info_json:
        results = compare_obj.compare_anchors_with_query(query_info=query_info)
        new_results = dict(results)
        all_results.append(new_results)

    # for query_img in os.listdir(DIR_OF_QUERIES_IMGS):
    #     query_img_path = f"{DIR_OF_QUERIES_IMGS}/{query_img}"
    #     results = compare_obj.compare_anchors_with_query(query_img_path=query_img_path)
    #

    save_dir = f'reports/{CLIENT}'
    pathlib.Path(save_dir).mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_results).to_csv(f'{save_dir}/scrapped_images_vs_anchors_{STORE}.csv', index=False)
    print("*" * 50 + "\n" + "END")