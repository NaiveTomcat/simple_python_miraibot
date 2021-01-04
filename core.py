import requests
import json
from urllib.request import urlretrieve
import urllib
import os
import time
import pgmagick

from config import *


def getAcgGovSearch(query,offset=None):
    headers = {'token': AcgGov_token, 'referer': 'https://www.acg-gov.com'}
    url = 'https://api.acg-gov.com/public/search?%s' % urllib.parse.urlencode({'q': query})

    if offset is not None:
        url += '&offset=%i' % offset
    log(url)
    r = requests.get(url, headers=headers)
    return r.json()['illusts']


def getAcgGovSetu():
    headers = {'token': AcgGov_token, 'referer': 'https://www.acg-gov.com'}
    url = 'https://api.acg-gov.com/public/setu'
    r = requests.get(url, headers=headers)
    return r.json()['data']


def getAcgGovRank(mode='day'):
    headers = {'token': AcgGov_token, 'referer': 'https://www.acg-gov.com'}
    date = time.strftime("%Y-%m-%d", time.localtime(time.time()-60*60*24))
    url = 'https://api.acg-gov.com/illusts/ranking?mode=' + mode +'&date=' + date
    r = requests.get(url, headers=headers)
    # log(r.json())
    return r.json()['illusts']


def getAcgGovId(id='12345'):
    headers = {'authorization': AcgGov_token,'token': AcgGov_token,
               'referer': 'https://www.acg-gov.com'}
    url = 'https://api.acg-gov.com/illusts/detail?illustId='+id+'&reduction=true'
    r = requests.get(url, headers=headers)
    log(r.json())
    return r.json()['data']['illust']


def getpic(apikey, r18=False, keyword=None):
    url = 'https://api.lolicon.app/setu/'+'?apikey='+apikey
    if r18:
        url += '&r18=1'
    if keyword is not None:
        url += '&keyword='+keyword
    # log(url)
    r = requests.get(url)
    # log(r.json())
    if r.status_code == 200 and r.json()['code'] == 0:
        log('lolicon success')
        return r.json()['data'][0], r.json()['quota'], None

    else:
        log('lolicon failed')
        return None, r.json()['quota_min_ttl'], r.json()['code']


def getpicpixiv(mode):
    url = 'https://api.loli.st/pixiv/?mode=' + mode
    r = requests.get(url)
    if r.status_code == 200:
        log('pixiv success')
        return r.json()
    else:
        log('pixiv failed')
        # log(r.content.decode('utf-8'))
        return None


def auth(authkey):
    url = mirai_url + '/auth'
    payload = {'authKey': authkey}
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    # log(r.json())
    if r.status_code == 200 and r.json()['code'] == 0:
        log('auth success')
        return r.json()['session']
    else:
        log('auth failed')
        return None


def verify(sessionKey, qq):
    url = mirai_url + '/verify'
    payload = {'sessionKey': sessionKey, 'qq': qq}
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    if r.status_code == 200 and r.json()['code'] == 0:
        log('verify success')
        return True
    else:
        log('verify failed')
        return False


def sendGroupMessage(sessionKey, target, picurl, text='图来了', headers=None):
    time.sleep(0.25)
    log(picurl)
    try:
        if picurl is not None:
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)
            timestr = str(time.time())
            picpath = os.path.join(temp_path, 'temp'+timestr+os.path.splitext(picurl)[1])
            ppicpath = os.path.join(temp_path, 'tmp'+timestr+'.png')
            log(picpath)
            # urlretrieve(picurl,filename=picpath)
            if headers is None:
                r = requests.get(picurl)
            else:
                r = requests.get(picurl, headers=headers)
            if r.status_code != 200:
                log(r.status_code)
                log('Failed to download',r.url)
                return
            with open(picpath, 'wb') as outfile:
                outfile.write(r.content)
                # outfile.write(b'Processed by NaiveTomcat')
            # command = 'cat '+picpath+' '+'/home/tomdang/setubot/mirai/core/data/net.mamoe.mirai-api-http/images/xyx.gif'+' > '+ppicpath
            # os.system(command)
            im = pgmagick.Image(picpath)
            # im.quality(100)
            im.write(ppicpath)
            log(ppicpath)
            url = mirai_url + '/sendGroupMessage'
            payload = {'sessionKey': sessionKey, 'target': target, 'messageChain': [
                {'type': 'Plain', 'text': text}, {'type': 'Image', 'path': 'temp'+timestr+os.path.splitext(picurl)[1]},{'type': 'Plain', 'text': ('URL: '+picurl)}]}
        else:
            picpath = None
            url = mirai_url + '/sendGroupMessage'
            payload = {'sessionKey': sessionKey, 'target': target, 'messageChain': [{'type': 'Plain', 'text':'Result:\n'},{'type': 'Plain', 'text': text}]}
        # log(payload)
        # log(json.dumps(payload))
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        # log(r.json())
        if r.status_code == 200 and r.json()['code'] == 0:
            log('Sent success')
        else:
            log('Failed to send')
            log(r.content)
        if picpath is not None:
            os.remove(picpath)
    finally:
        pass


def release(session, qq):
    url = mirai_url + '/release'
    payload = {'sessionKey': session, 'qq': qq}
    headers = {'Content-Type': 'application/json'}
    requests.post(url, headers=headers, data=json.dumps(payload))


def checkurl(url):
    r = requests.get(url)
    return r.status_code == 200


def main():
    session = auth(mirai_authkey)
    verify(session, mirai_qq)
    picurl,_,_ = getpic(lolicon_apikey)
    picurl = picurl['url']
    # picurl = 'https://i.pixiv.cat/img-original/img/2020/07/04/11/09/56/82740006_p0.jpg'
    if checkurl(picurl):
        sendGroupMessage(session, target_group, picurl)
    release(session, mirai_qq)


if __name__ == '__main__':
    main()
