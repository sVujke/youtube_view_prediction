
# coding: utf-8

from api_key import KEY
from urllib.parse import urlencode
import requests
import json
from datetime import datetime
import tqdm
import time
import pandas as pd 
import sys


def handle_response(url, params_dict):
    """ Sends request with specified params, returns list of items and nextPageToken
    """
    url = url+"?"+urlencode(params_dict)
    resp = requests.get(url)
#     print(resp)
    response_dict = json.loads(resp.text)
    if "nextPageToken" in response_dict:
        return_dict = {
            "items": response_dict["items"],
            "nextPageToken": response_dict["nextPageToken"]
        }
    else: 
        return_dict = {
            "items": response_dict["items"],
            "nextPageToken": None
        }
    return return_dict


def get_all_playlist_items(params_dict):
    """ Returns all video ID's from specified Play List
    """
    item_ids = []
    stop = False
    while stop == False:
        url = "https://www.googleapis.com/youtube/v3/playlistItems"
        if item_ids == []:
            response = handle_response(url, params_dict)
            for item in response["items"]:
                item_ids.append(item["contentDetails"]['videoId'])
#                 print(item["contentDetails"]['videoId'])
            npt = response["nextPageToken"]
            # print("FIRST NPT: {}".format(npt))
        else: 
            params_dict["pageToken"] = npt
            response = handle_response(url, params_dict)
            for item in response["items"]:
                item_ids.append(item["contentDetails"]['videoId'])
            npt = response["nextPageToken"]
            # print("NPT: {}".format(npt))
            # print(len(response["items"]))
            if npt == None:
                stop = True
    return item_ids


def save_video_metadata(key, video_ids, path_pickle, path_responses):
    """ Returns a dataframe with metadata and saves all responses in a json file 
    """
    resp_lst = []
    endpoint = "https://www.googleapis.com/youtube/v3/videos" 
    metadata_lst = []
    for video_id in tqdm.tqdm(video_ids):
        params = {
                    'id': video_id,
                    'part': 'id, snippet, contentDetails, player, statistics, status',
                    'key': key,
                }
#         print(params)
        url = endpoint + "?" + urlencode(params)
#         print(url)
#         time.sleep(0.5)
        resp = requests.get(url)
        response_dict = json.loads(resp.text)
        resp_lst.append(response_dict)
#         print(response_dict.keys())
        title = response_dict["items"][0]["snippet"]["title"]
        stats = response_dict["items"][0]["statistics"]
        comments = stats['commentCount']
        dislikes = stats['dislikeCount']
        favourites = stats['favoriteCount']
        likes = stats['likeCount']
        views = stats['viewCount']
        tags = response_dict["items"][0]["snippet"]["tags"]
        published = datetime.strptime(response_dict["items"][0]["snippet"]["publishedAt"].split("T")[0], '%Y-%m-%d')
        sub_lst = [title, published, tags, comments, likes, dislikes, favourites, views]
        metadata_lst.append(sub_lst)
    df = pd.DataFrame(metadata_lst)
    df.columns = ["title", "published", "tags", "comments", "likes", "dislikes", "favourites", "views"]
    df.to_pickle(path_pickle)
    print("Pickle saved at {} \n".format(path_pickle))
    with open(path_responses, 'w') as outfile:
        json.dump(resp_lst, outfile)
    print("Responses saved at {} \n".format(path_responses))


def main():

    PLAYLIST_ID = 'PLQPfsdgAXeMlB0vNrePI1qfhjSt91yShn'

    playlist = sys.argv[1]
    if playlist == "1":
        pass
    else:
        PLAYLIST_ID = playlist 
    path_pickle = sys.argv[2]
    path_responses = sys.argv[3]

    print(PLAYLIST_ID)

    params = {
            'playlistId': PLAYLIST_ID,
            'part': 'id, snippet, contentDetails, status',
            'maxResults': 50,
            'key': KEY,
        }

    video_ids = get_all_playlist_items(params)

    print("Number of fetched videos in playlist: {}".format(len(video_ids)))

    save_video_metadata(KEY, video_ids, path_pickle, path_responses)


if __name__ == '__main__':
    main()


