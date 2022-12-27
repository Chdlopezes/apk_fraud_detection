# Apk inference tool

To perform app logos comparison. 

## How it works:
1. Scrap in the principal app companies: Appstore and Google Play web pages looking for all the app logos obtained for a
 search query.
   - This search query is intended to be for a client mobile application. For example: 'Banco Americas' 

2. All mobile application logos found are stored in data/scrap directory.
3. For each client there's a directory: '_data/anchors/{client}/_' which contains legitimate logos for each client mobile application.
4. The model perform a similarity analysis between each image (app logo) downloaded in the scrap process (steps 1-2) with 
respect to the anchors or legitimate logos for the corresponding client. For each logo image pair a similarity score is computed.
5. The similarity scores for each scrapped image w.r.t anchors or legitimate images are reported in a .csv file in reports/ directory.

## to run

1. Set the search query by editing the file: `client_query.json`. This file will contain two keys: 'client' and 'store'.
 - Set 'client' value with the name of the client: i.e. 'banco cliente'.
 - Set 'store' value with the name of the mobile application store: Valid values are: 'appstore' or 'googlePlay'.

2. Run the docker image by opening a terminal in the directory where `docker_compose.yml` is located
and run: __docker-compose up --build__ (for the first time) or simply 
__docker-compose up__ the second and subsequent times. 

__(Note)__: If for a given client and store specified in `client_query.json`, there's not an anchor file stored. Then an Exception
will raise with the message that this file does not exist. 

## modules and scripts

1. `comparisson_client.py`: Is the main module. This module contains a class named ComparissonClient 
     which can be used to perform all scrap process from a given query (specified in client_query.json file.
     Also performs the images comparison process from client query scrapped images with respect to the anchors
     stored at "data/anchors" path. Finally it can be used to export the results in a csv file, by default the results
     will be exported to "reports/query_results.csv"

2. `image_processor_modules`: In this module you will find a set of tools that are used to perform the image comparison
 process. These functions are constructed based on opencv library tools. They process a query image, and compare it with an
 anchor image which correspond to the same client.

3. `study_processor_modules`: This module aggregate all results from image comparisson performed with the modules in `image_processor_modules.py`
and compute statistic tendency measures for them, in order to produce a final result called 'score' for each app image pair (scrapped image vs anchor image).

4. `scrap_all_clients.py`: This module could be used if you don't want to use the client_query.json file, instead all clients
 in the file 'files/clients.json' are called at the same time for the app logos comparison process.
 
5. `srap_appstore.py`: This module contains the steps performed in the scrap process for a client query which is search in
    appstore webpage. Store images are located at "data/images/scrap/appstore/{client_name}/images/" 

6. `srap_googlePlay.py`: This module contains the steps performed in the scrap process for a client query which is search in
    Google Play webpage. Store images are located at "data/images/scrap/googlePlay/{client_name}/images/"
7. `scrap_stores.py`: Use this module to call `scrap_appstore.py` and `scrap_googlePlay.py` at the same time.



