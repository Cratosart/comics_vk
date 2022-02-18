import os
import random
import requests
import urllib
import urllib.parse
import urllib.request

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
    image_url = comics.get('img')
    comments = comics.get('alt')
    return image_url, comments


def get_upload_url(access_token, group_id):
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
    upload_url = response.json()
    check_vk_status(upload_url)
    return upload_url['response']['upload_url']


def upload_image(upload_url, path):
    with open(path, 'rb') as file:
        files = {'photo': file}
        response = requests.post(upload_url, files=files)
    response.raise_for_status()
    image_info = response.json()
    check_vk_status(image_info)
    return image_info['photo'], \
        image_info['server'], \
        image_info['hash']


def save_image(url, images_path, filename):
    os.makedirs(images_path, exist_ok=True)
    urllib.request.urlretrieve(url, f'{images_path}/{filename}')


def save_vk_photo(photo, access_token, server, group_id, hash_img):
    payload = {
        'access_token': access_token,
        'group_id': group_id,
        'photo': photo,
        'server': server,
        'hash': hash_img,
        'v': '5.131'
    }
    url_save_photo_vk = 'https://api.vk.com/method/photos.saveWallPhoto'
    response = requests.post(url_save_photo_vk, params=payload)
    response.raise_for_status()
    identifiers = response.json()['response'][0]
    owner_id = identifiers.get('owner_id')
    media_id = identifiers.get('id')
    check_vk_status(response)
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
    check_vk_status(response)


def check_vk_status(response):
    if 'error' in response:
        raise requests.exceptions.HTTPError(response['error']['error_msg'])


if __name__ == '__main__':
        load_dotenv()
        client_id = os.getenv('CLIENT_ID')
        access_token = os.getenv('ACCESS_TOKEN')
        group_id = os.getenv('GROUP_ID')
        images_path = './images_comics'
        filename = 'image.png'
        num = identify_the_latest_comic(url='https://xkcd.com/info.0.json')
        id_comic = random.randint(1, num)
        try:
            upload_url = get_upload_url(access_token, group_id)
            image_url, comments = get_comics(id_comic)
            save_image(image_url, images_path, filename)
            photo, server, hash_img = upload_image(
                upload_url,
                f'{images_path}/{filename}'
                )
            owner_id, media_id = save_vk_photo(
                photo,
                access_token,
                server,
                group_id, hash_img)
            post_wall_vk(
                group_id,
                access_token,
                owner_id,
                media_id,
                comments)
        finally:
            os.remove(f'{images_path}/{filename}')
