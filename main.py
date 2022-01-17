import json
import time
import hashlib
import pathlib
import requests
from functools import lru_cache


@lru_cache(1)
def get_token(token_file='token.txt'):
    with open(token_file) as fr:
        token = fr.read().strip()
    return token


@lru_cache(1)
def get_devices(recache=False):
    headers = {
        'Access-Token': get_token(),
    }
    response = requests.get('https://api.pushbullet.com/v2/devices', headers=headers)
    return json.loads(response.text)['devices']


@lru_cache(1)
def get_specific_device_iden(nickname='Google Pixel 6'):
    for device in get_devices():
        if device['nickname'] == nickname:
            return device['iden']
    raise ValueError(f'Device with nickname {nickname} not found!')


def push_notification_to_device(title, body, nickname='all'):
    headers = {
        'Access-Token': get_token(),
        'Content-Type': 'application/json'
    }
    data = {
        "body": body, 
        "title": title, 
        "type": "note",
    }
    if not nickname == 'all':
        data['device_iden'] = get_specific_device_iden(nickname)
    push_link = 'https://api.pushbullet.com/v2/pushes'
    response = requests.post(push_link, headers=headers, data=json.dumps(data))
    if not response.status_code == 200:
        fname = f'{hashlib.sha1(str(time.time()).encode()).hexdigest()}.log'
        p = pathlib.Path('logs/') / fname
        with open(p, 'w') as fw:
            fw.write(response.text)
        raise requests.exceptions.HTTPError(
            f'[{response.status_code}] Something went wrong, response text can be found here: {str(p.resolve())}'
        )


if __name__ == '__main__':
    push_notification_to_device('sample text', 'sample text')
