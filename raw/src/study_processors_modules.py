import os
import pandas as pd
import numpy as np
from src.image_processor_modules import load_and_process_img
from src.image_processor_modules import descriptor_matches
from src.image_processor_modules import other_distances
from src.image_processor_modules import other_similarities
from src.image_processor_modules import color_similarities
from src.image_processor_modules import color_distances


def create_study(anchors_path, query_img_path, query_img_name):
    """
    This function performs a series of image comparison methods using mainly opencv library in order to capture the
    similarities and differences between each pair of images compared. Receives a query image which comes from a scrap
    search for a given client and compares it with all anchors of that client.

    @param anchors_path: (str) Path of the client anchors.
    @param query_img_path: (str) Path of the scrap image downloaded from the scrap process
    @param query_img_name: (str) A string used as an image identifier.
    @return: (dict) A Dictionary containing all the similarity and distance metrics between query image and each anchor.
    """
    adir = anchors_path
    study = []
    if len([ai for ai in os.listdir(adir) if ai.endswith('.png')]) == 0:
        raise FileNotFoundError(f'Theres not anchors in the directory: {adir}')

    for aimname in [ai for ai in os.listdir(adir) if ai.endswith('.png')]:
        qimpath = query_img_path
        assert qimpath.endswith('.png'), "Not a png image format provided"
        aimpath = f'{adir}/{aimname}'
        owned = np.nan
        for th in range(90, 230, 10):  # (90, 215, 5):
            for k in range(3, 9, 2):  # (3, 13, 2):
                aimg = load_and_process_img(aimpath, 'anchor', th, k)
                qimg = load_and_process_img(qimpath, 'query', th, k)
                # Pregunta. No debería ser aimpath en alguna de las dos lineas siguientes?
                acimg = load_and_process_img(aimpath, 'anchor', th, k, keep_color=True)
                qcimg = load_and_process_img(qimpath, 'query', th, k, keep_color=True)

                n, m = descriptor_matches(aimg, qimg)
                similarities = other_similarities(aimg, qimg)
                distances = other_distances(aimg, qimg)
                c_similarities = color_similarities(acimg, qcimg)
                c_distances = color_distances(acimg, qcimg)
                row = {
                    'path': qimpath,
                    'name': query_img_name,
                    'orb_matches_sim': n,
                    'orb_mean_dist': m,
                    'owned': owned,
                }
                row = row | similarities
                row = row | distances
                row = row | c_similarities
                row = row | c_distances

                study.append(row)
    return study


def process_study(study_, output='list'):
    """
    This functions receives the study computed for a set of images using function 'create_study' and performs some
    processing such as normalization. For this process the input dictionary is converted to pandas.Dataframe and then
    the results are returned as list of dictionaries or a Dataframe, according output parameter.
    @param study_: (dict) Dictionary containing all metrics computed in an image comparison process (using create_study)
    @param output: (str) Format of the output. Possible values: 'list': List of dictionaries, 'df': pandas.Dataframe
    @return: Processed metrics for each image comparison. (list of dicts or pandas Dataframe) depending on output param.
    """
    if isinstance(study_, list):
        if not study_:
            return pd.DataFrame([])
        else:
            _df = pd.DataFrame(study_)
    elif isinstance(study_, pd.DataFrame):
        if study_.empty:
            return pd.DataFrame([])
        else:
            _df = study_.copy(deep=True)
    else:
        raise TypeError('list or pd.DataFrame object type must be passed')

    for col in _df.columns:
        if ('sim' in col) or ('dist' in col):
            _df[col] = _df[col] / _df[col].max()
        if 'dist' in col:
            _df[col] = 1 - _df[col]

    if output == 'df':
        return _df
    elif output == 'list':
        return _df.to_dict(orient='records')
    else:
        raise TypeError("output param must be 'list' or 'df'")


def agg_study(study):
    """
    If there are many anchors to compare with, for each metric the mean is computed. i.e. for a metric m, comparing a
    query image with n anchors we have: m_1,...m_n, where m_i is the value for the metric m when comparing the query
    image with the anchor i. Then a dataframe with all the metrics mean is output. Each row corresponding to each query
    image.
    @param study: (dict) Dictionary containing the image comparison metrics (using create_study) or normalized metrics
    (create_study -> process_study).
    @return: Dataframe in which each row corresponds to the mean for each metric comparing a query image with a set of
    anchors.
    """
    if isinstance(study, list):
        if not study:
            return pd.DataFrame([])
        else:
            study_df = pd.DataFrame(study)
    elif isinstance(study, pd.DataFrame):
        if study.empty:
            return pd.DataFrame([])
        else:
            study_df = study.copy(deep=True)
    else:
        raise TypeError("output param must be 'list' or 'df'")

    sims_agg = pd.pivot_table(
        study_df,
        values=[
            'owned', 'orb_matches_sim', 'ssim_sim',
            'uqi_sim', 'msssim_sim', 'scc_sim', 'vifp_sim',
        ],
        index='name',
        aggfunc={
            'owned': np.mean,
            'orb_matches_sim': max,
            'ssim_sim': np.mean,
            'uqi_sim': np.mean,
            'msssim_sim': np.mean,
            'scc_sim': np.mean,
            'vifp_sim': np.mean,
        }
    )

    dists_agg = pd.pivot_table(
        study_df,
        values=[
            'orb_mean_dist', 'rmse_dist', 'ergas_dist',
            'sam_dist',
        ],
        index='name',
        aggfunc={
            'orb_mean_dist': np.mean,
            'rmse_dist': np.mean,
            'ergas_dist': np.mean,
            'sam_dist': np.mean,
        }
    )

    all_agg_study = pd.concat(
        [sims_agg, dists_agg], axis=1
    ).reset_index(drop=False)

    return all_agg_study


def process_agg(_, output='list'):
    if isinstance(_, list):
        if not _:
            return pd.DataFrame([])
        else:
            _df = pd.DataFrame(_)
    elif isinstance(_, pd.DataFrame):
        if _.empty:
            return pd.DataFrame([])
        else:
            _df = _.copy(deep=True)
    else:
        raise TypeError('list or pd.DataFrame object type must be passed')

    for col in _df.columns:
        if ('sim' in col) or ('dist' in col):
            _df[col] = _df[col]/_df[col].max()

    if output == 'df':
        return _df
    elif output == 'list':
        return _df.to_dict(orient='records')
    else:
        raise TypeError("output param must be 'list' or 'df'")


def collapse_agg(agg):
    """
    This function takes the aggregate dataframe computed at 'agg_study' function and computes the mean for all of these
    metrics. This value will correspond to the reported score: value between (0,1) of similarity of the query image
    with respect to all anchors of the client.
    @param agg: (pandas.Dataframe) Dataframe with the aggregate image comparison metrics obtained in 'agg_study'
    function.
    @return: Dataframe in which each row corresponds to the query image and a column named 'score' with the result of
    the comparison for that query image w.r.t a set of images (for this project the set of anchors of a given client).
    """
    if isinstance(agg, list):
        if not agg:
            return pd.DataFrame([])
        agg = pd.DataFrame(agg)
    elif isinstance(agg, pd.DataFrame):
        if agg.empty:
            return pd.DataFrame([])
        else:
            agg = agg.copy(deep=True)
    else:
        raise TypeError('list or pd.DataFrame object type must be passed')

    if 'owned' in agg.columns:
        agg_index = agg[['name', 'owned']]
        agg_metrics = agg.drop(columns=['name', 'owned'])
    else:
        agg_index = agg[['name']]
        agg_metrics = agg.drop(columns=['name'])

    collapsed_metrics = agg_metrics.mean(axis=1)
    collapsed = pd.concat([agg_index, collapsed_metrics], axis=1)
    collapsed = collapsed.rename(columns={0: 'score'})

    return collapsed