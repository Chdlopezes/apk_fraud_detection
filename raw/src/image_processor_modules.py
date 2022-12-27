import cv2
import numpy as np
import sewar.full_ref


def process_img(image, img_role, th, k, IMSHOW, keep_color=False):
    """
    Processes an image using opencv methods.
    :param image: (np.array) image to process
    :param img_role: (str) anchor or query
    :param th: (int) in [0, 255]
    :param k: odd (int)
    :param IMSHOW: (bool) to display images or not to
    :param keep_color: (bool) to process images with color or not
    :return thresh: (np.array) processed image
    """
    try:
        image = image[18:-18, 18:-18]
    except TypeError:
        image = np.zeros((256, 256, 3), np.uint8)[18:-18, 18:-18]
        print('no image loaded')

    if not keep_color:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (k, k), 0)
        thresh = cv2.threshold(blurred, th, 255, cv2.THRESH_BINARY_INV)[1]
    else:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        blurred = cv2.GaussianBlur(rgb, (k, k), 0)
        thresh = blurred  # Sorry for this. Only for consistency.

    if IMSHOW:
        cv2.imshow(f'input_{img_role}', image)
        cv2.imshow(f'output_{img_role}', thresh)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return thresh


def load_and_process_img(img_path, img_role, th, k, keep_color=False):
    """
    Loads and processes an image.
    :param img_path: (str) path of image to process
    :param img_role: (str) anchor or query
    :param th: (int) in [0, 255]
    :param k: odd (int)
    :return processed_img: (np.array) processed image
    """
    IMSHOW = False
    img = cv2.imread(img_path)
    processed_img = process_img(img, img_role, th, k, IMSHOW, keep_color)
    return processed_img


def descriptor_matches(anchor_img, query_img):
    """
    Computes ORB descriptors and their statistics.
    :param anchor_img: (np.array) image to compare against
    :param query_img: (np.array) image to compare
    :return n_matches: (int) number of ORB matched key points between images
    :return distance_mean: (float) mean distance of matched key points
    """
    orb = cv2.ORB_create()
    anchor_kp, anchor_des = orb.detectAndCompute(anchor_img, None)
    query_kp, query_des = orb.detectAndCompute(query_img, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING)

    try:
        matches = bf.knnMatch(anchor_des, query_des, k=2)
        good_to_continue = True
    except Exception as E:
        print(f"Couldn't get matches: {E}")
        matches = [['not', 'good']]
        good_to_continue = False

    if not good_to_continue:
        n_matches = 0
        distance_mean = np.nan
    else:
        good_matches = []
        for tup in matches:
            if len(tup) != 2:
                continue
            m, n = tup
            if m.distance < (0.75 * n.distance):
                good_matches.append([m])

        n_matches = len(good_matches)
        distance_mean = np.mean([m[0].distance for m in good_matches])

    return n_matches, distance_mean


def other_similarities(anchor_img, query_img):

    try:
        ssim_sim = np.mean(sewar.full_ref.ssim(anchor_img, query_img))
    except:
        ssim_sim = (np.nan, np.nan)
    try:
        uqi_sim = sewar.full_ref.uqi(anchor_img, query_img)
    except:
        uqi_sim = np.nan
    try:
        msssim_sim = sewar.full_ref.msssim(anchor_img, query_img)
    except:
        msssim_sim = np.nan
    try:
        scc_sim = sewar.full_ref.scc(anchor_img, query_img)
    except:
        scc_sim = np.nan
    try:
        vifp_sim = sewar.full_ref.vifp(anchor_img, query_img)
    except:
        vifp_sim = np.nan

    similarities = {
        'ssim_sim': np.mean(ssim_sim),
        'uqi_sim': uqi_sim,
        'msssim_sim': abs(msssim_sim),
        'scc_sim': scc_sim,
        'vifp_sim': vifp_sim,
    }

    return similarities


def other_distances(anchor_img, query_img):
    try:
        rmse_dist = sewar.full_ref.rmse(anchor_img, query_img)
    except:
        rmse_dist = np.nan
    try:
        ergas_dist = sewar.full_ref.ergas(anchor_img, query_img)
    except:
        ergas_dist = np.nan
    try:
        sam_dist = sewar.full_ref.sam(anchor_img, query_img)
    except:
        sam_dist = np.nan

    distances = {
        'rmse_dist': rmse_dist,
        'ergas_dist': ergas_dist,
        'sam_dist': sam_dist,
    }

    return distances


def color_compare(anchor_img, query_img, type):
    anchor_hist = cv2.calcHist([anchor_img], [0, 1, 2], None, [10, 10, 10])
    anchor_hist = cv2.normalize(anchor_hist, anchor_hist).flatten()

    query_hist = cv2.calcHist([query_img], [0, 1, 2], None, [10, 10, 10])
    query_hist = cv2.normalize(query_hist, query_hist).flatten()

    if type == 'sim':
        methods = {
            "correlation": cv2.HISTCMP_CORREL,
            "intersection": cv2.HISTCMP_INTERSECT
        }
    elif type == 'dist':
        methods = {
            "chi2": cv2.HISTCMP_CHISQR,
            "hellinger": cv2.HISTCMP_BHATTACHARYYA,
        }
    else:
        raise NotImplementedError("type param must be 'dist' or 'sim'")

    results = {}
    for method_name, method in methods.items():
        result = cv2.compareHist(anchor_hist, query_hist, method)
        results[method_name] = result

    return results


def color_similarities(anchor_img, query_img):
    try:
        color_sims = color_compare(anchor_img, query_img, 'sim')
        color_corr_sim = color_sims['correlation']
        color_int_sim = color_sims['intersection']
    except:
        color_corr_sim = np.nan
        color_int_sim = np.nan

    similarities = {
        'color_corr_sim': color_corr_sim,
        'color_int_sim': color_int_sim
    }

    return similarities


def color_distances(anchor_img, query_img):
    try:
        color_dists = color_compare(anchor_img, query_img, 'dist')
        color_chi2_dist = color_dists['chi2']
        color_helli_dist = color_dists['hellinger']
    except:
        color_chi2_dist = np.nan
        color_helli_dist = np.nan

    distances = {
        'color_chi2_dist': color_chi2_dist,
        'color_helli_dist': color_helli_dist
    }
    return distances