import requests
import os
import urllib
import urllib.parse
import urllib.request
import random

from dotenv import load_dotenv
from pathlib import Path


def identify_the_latest_comic(url):
    comics = requests.get(url)
    comics.raise_for_status()
    comics = comics.json()
    return comics['num']


def get_comics(id_comic):
    url = f'https://xkcd.com/{id_comic}/info.0.json'
    comics = requests.get(url)
    comics.raise_for_status()
    comics = comics.json()
    image_url = comics.get('img', None)
    comments = comics.get('alt', None)
    return image_url, comments


def get_upload_url(
        access_token,
        group_id):
    payload = {
        'access_token': access_token,
        'group_id': group_id,
        'v': '5.131',
        'extended': '1'
    }
    url_vk = 'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(
        url_vk,
        params=payload)
    response.raise_for_status()
    response = response .json()
    return response['response']['upload_url']


def upload_image(upload_url):
    path = './images_comics/image.png'
    with open(path, 'rb') as file:
        url = upload_url
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
        response = response.json()
        return response['photo'], \
            response['server'], \
            response['hash']


def save_image(url):
    images_path = 'images_comics'
    os.makedirs(images_path, exist_ok=True)
    filename = 'image'
    path = f'./{images_path}/{filename}.png'
    urllib.request.urlretrieve(url, path)


def save_vk_photo(
        photo,
        access_token,
        server,
        group_id,
        hash):
    payload = {
        'access_token': access_token,
        'group_id': group_id,
        'photo': photo,
        'server': server,
        'hash': hash,
        'v': '5.131'
    }
    url_save_photo_vk = 'https://api.vk.com/method/photos.saveWallPhoto'
    response = requests.post(
        url_save_photo_vk,
        params=payload)
    response.raise_for_status()
    identifiers = response.json()['response']
    for element in identifiers:
        owner_id = element.get('owner_id', None)
        media_id = element.get('id', None)
    return owner_id, media_id


def post_wall_vk(
        group_id,
        access_token,
        owner_id,
        media_id,
        comments):
    payload = {
        'owner_id': f'-{group_id}',
        'access_token': access_token,
        'from_group': group_id,
        'attachments': f'photo{owner_id}_{media_id}',
        'message': comments,
        'v': '5.131'
    }
    url_wall = 'https://api.vk.com/method/wall.post'
    response = requests.post(url_wall, params=payload)
    response.raise_for_status()


if __name__ == '__main__':
    load_dotenv()
    client_id = os.getenv('CLIENT_ID')
    access_token = os.getenv('ACCESS_TOKEN')
    group_id = os.getenv('GROUP_ID')
    num = identify_the_latest_comic(url='https://xkcd.com/info.0.json')
    id_comic = random.randint(1, num)
    upload_url = get_upload_url(access_token, group_id)
    image_url, comments = get_comics(id_comic)
    save_image(image_url)
    photo, server, hash = upload_image(upload_url)
    owner_id, media_id = save_vk_photo(
        photo,
        access_token,
        server,
        group_id, hash)
    post_wall_vk(
        group_id,
        access_token,
        owner_id,
        media_id,
        comments)
    os.remove('./images_comics/image.png')
