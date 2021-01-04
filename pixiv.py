from pixivapi import Client, Size
import random
from os import path
import pathlib
from pixivconfig import *
from config import temp_path

client = Client()


def __init__():
    client.login(username, password)


def getUrl(origin='https://i.pximg.net/'):
    return origin.replace('pximg.net','pixiv.cat')


def getRecommended():
    illus = client.fetch_illustrations_recommended()
    illu = illus['illustrations'][random.randint(
        0, len(illus['illustrations'])-1)]
    p = path.join(temp_path, 'pixiv')
    p = pathlib.Path(p)
    # illu.download(p)
    # ext = path.splitext(illu.image_urls[Size.ORIGINAL])[1]
    # print(illu.image_urls)
    return illu, getUrl(illu.image_urls[Size.ORIGINAL])

if __name__ == '__main__':
    __init__()
    print(getRecommended())
