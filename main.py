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


def get_comics(url):
    comics = requests.get(url)
    comics.raise_for_status()
    comics = comics.json()
    for key, value in comics.items():
        if key == 'img':
            image_url = value
    for key, value in comics.items():
        if key == 'alt':
            comments = value
    return image_url, comments


def get_upload_url(
        url_vk,
        access_token,
        group_id):
    payload = {
        'access_token': access_token,
        'group_id': group_id,
        'v': '5.131',
        'extended': '1'
    }
    vk_group = requests.get(
        url_vk,
        params=payload)
    vk_group.raise_for_status()
    vk_group = vk_group.json()
    return vk_group['response']['upload_url']


def upload_image(upload_url):
    with open('./images_comics/test.png', 'rb') as file:
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
    filename = 'test'
    urllib.request.urlretrieve(url, f'./{images_path}/{filename}.png')


def save_vk_photo(
        url_save_photo_vk,
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
    response = requests.post(
        url_save_photo_vk,
        params=payload)
    response.raise_for_status()
    params = response.json()['response']
    for element in params:
        for key, value in element.items():
            if key == 'owner_id':
                owner_id = value
            if key == 'id':
                media_id = value
    return owner_id, media_id


def post_wall_vk(
        url_wall,
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
    response = requests.post(url_wall, params=payload)
    response.raise_for_status()


if __name__ == '__main__':
    load_dotenv()
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    client_id = os.getenv('CLIENT_ID')
    access_token = os.getenv('ACCESS_TOKEN')
    group_id = os.getenv('GROUP_ID')
    num = identify_the_latest_comic(url='https://xkcd.com/info.0.json')
    id_comic = random.randint(1, num)
    url = f'https://xkcd.com/{id_comic}/info.0.json'
    url_vk = 'https://api.vk.com/method/photos.getWallUploadServer'
    upload_url = get_upload_url(url_vk, access_token, group_id)
    url_save_photo_vk = 'https://api.vk.com/method/photos.saveWallPhoto'
    image_url, comments = get_comics(url)
    save_image(image_url)
    photo, server, hash = upload_image(upload_url)
    owner_id, media_id = save_vk_photo(
        url_save_photo_vk,
        photo,
        access_token,
        server,
        group_id, hash)
    url_wall = 'https://api.vk.com/method/wall.post'
    post_wall_vk(
        url_wall,
        group_id,
        access_token,
        owner_id,
        media_id,
        comments)
    os.remove('./images_comics/test.png')
