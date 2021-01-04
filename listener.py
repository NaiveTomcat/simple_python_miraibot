from flask import Flask, escape, url_for, request
import json
from config import mirai_authkey, mirai_qq, lolicon_apikey, target_group, log,\
    commanders
from core import auth, verify, getpic, checkurl, release, sendGroupMessage,\
    getAcgGovSetu, getAcgGovId, getAcgGovRank, getAcgGovSearch
import pixiv
import os

app = Flask(__name__)


@app.route('/post', methods=['POST'])
def checkAndSend():
    try:
        return {'code': 0}
    finally:
        try:
            data = json.loads(request.data.decode())
            # log(data)
            if data['type'] == 'GroupMessage' and data['sender']['group']['id'] == target_group:
                messageChain = data['messageChain']
                r18 = False
                for message in messageChain:
                    if message['type'] == 'At' and message['target'] == mirai_qq:
                        r18 = True
                    if message['type'] == 'Plain' and ('来点图' in message['text'] or '来张图' in message['text']
                                                       or 'h' == message['text'] or ' h' == message['text']):
                        session = auth(mirai_authkey)
                        verify(session, mirai_qq)
                        pic, quota, statusCode = getpic(lolicon_apikey, r18)
                        if statusCode is not None:
                            sendGroupMessage(
                                session, target_group,
                                'http://127.0.0.1/xyx.gif',
                                '没搜到' if statusCode == 404 else'配额用完了，下一张图还要'+str(quota)+'秒')
                            return {'code': 0}
                        picurl = pic['url']
                        msg = '标题：'+pic['title']+'\npid：' + \
                            str(pic['pid']) +\
                            '\n画师：'+str(pic['author']) +\
                            '\nuid：'+str(pic['uid']) +\
                            '\ntags: '+'\n'.join(pic['tags']) + '\n' +\
                            '\n配额还有'+str(quota)+'张'
                        if checkurl(picurl):
                            sendGroupMessage(
                                session, target_group, picurl, msg)
                        release(session, mirai_qq)
                    if message['type'] == 'Plain' and '搜图：' in message['text'][:4]:
                        session = auth(mirai_authkey)
                        verify(session, mirai_qq)
                        keyword = message['text'][3:]
                        if keyword[0] == '：':
                            keyword = keyword[1:]
                        pic, quota, statusCode = getpic(
                            lolicon_apikey, r18, keyword)
                        # log('lolicon状态', statusCode)
                        if statusCode is not None:
                            sendGroupMessage(
                                session, target_group,
                                'http://127.0.0.1/xyx.gif',
                                '没搜到' if statusCode == 404 else'配额用完了，下一张图还要'+str(quota)+'秒')
                            return {'code': 0}
                        picurl = pic['url']
                        msg = '标题：'+pic['title']+'\npid：' + \
                            str(pic['pid']) +\
                            '\n画师：'+str(pic['author']) +\
                            '\nuid：'+str(pic['uid']) +\
                            '\ntags: '+'\n'.join(pic['tags']) + '\n' +\
                            '\n配额还有'+str(quota)+'张'
                        if checkurl(picurl):
                            sendGroupMessage(
                                session, target_group, picurl, msg)
                        release(session, mirai_qq)

                    if message['type'] == 'Plain' and 'setu' == message['text']:
                        headers = {'referer': 'https://www.acg-gov.com'}
                        session = auth(mirai_authkey)
                        verify(session, mirai_qq)
                        pic = getAcgGovSetu()
                        # log(pic)
                        picurls = pic['originals']
                        for index, picurl in enumerate(picurls):
                            tags = ''
                            for tag in pic['tags']:
                                tags += tag['name']
                                tags += '\n'
                            msg = '标题：'+pic['title']+'\npid：' + \
                                str(pic['illust']) +\
                                '\n画师：'+str(pic['user']['name']) +\
                                '\nuid：'+str(pic['user']['id']) +\
                                '\ntags：'+tags +\
                                '\n'+str(index+1)+'/'+str(pic['pageCount'])
                            if picurl is not None:
                                sendGroupMessage(
                                    session, target_group, picurl['url'], msg, headers)
                        release(session, mirai_qq)

                    if message['type'] == 'Plain' and ('看图 ' == message['text'][:3] or '看图：' == message['text'][:3]):
                        headers = {'referer': 'https://www.acg-gov.com'}
                        session = auth(mirai_authkey)
                        verify(session, mirai_qq)
                        pic = getAcgGovId(message['text'][3:])
                        log(pic)
                        if pic['page_count'] == 1:
                            index = 0
                            picurl = pic['meta_single_page']['original_image_url']
                            tags = ''
                            for tag in pic['tags']:
                                tags += tag['name']
                                tags += '\n'
                            msg = '标题：'+pic['title']+'\npid：' + \
                                str(pic['id']) +\
                                '\n画师：'+str(pic['user']['name']) +\
                                '\nuid：'+str(pic['user']['id']) +\
                                '\ntags：'+tags +\
                                '\n'+str(index+1)+'/'+str(pic['page_count'])
                            if picurl is not None:
                                sendGroupMessage(
                                    session, target_group, pixiv.getUrl(picurl), msg, headers)
                        else:
                            picurls = pic['meta_pages']
                            log(picurls)
                            for index, picurl in enumerate(picurls):
                                log(picurl)
                                tags = ''
                                for tag in pic['tags']:
                                    tags += tag['name']
                                    tags += '\n'
                                msg = '标题：'+pic['title']+'\npid：' + \
                                    str(pic['id']) +\
                                    '\n画师：'+str(pic['user']['name']) +\
                                    '\nuid：'+str(pic['user']['id']) +\
                                    '\ntags：'+tags +\
                                    '\n'+str(index+1)+'/' + \
                                    str(pic['page_count'])
                                if picurl is not None:
                                    sendGroupMessage(
                                        session, target_group, pixiv.getUrl(picurl['image_urls']['original']), msg, headers)
                        release(session, mirai_qq)

                    if message['type'] == 'Plain' and '搜索：' == message['text'][:3]:
                        headers = {'referer': 'https://www.acg-gov.com'}
                        session = auth(mirai_authkey)
                        verify(session, mirai_qq)
                        params = message['text'][3:]
                        try:
                            query, offset = params.split('^')
                            offset = int(offset)
                        except ValueError as e:
                            query = params
                            offset = 1
                        # offset = None
                        # try:
                        #     offset = int(params.split('^')[1])
                        # except Exception:
                        #     pass
                        log('after try')
                        pics = getAcgGovSearch(query, 30*(offset-1))
                        if pics == []:
                            sendGroupMessage(
                                session, target_group, 'http://127.0.0.1/xyx.gif', '没找到', headers)
                            release(session, mirai_qq)
                            return {'code': 0}
                        # log(pics)
                        for pic in pics:
                            # log(pic)
                            tags = ''
                            for tag in pic['tags']:
                                tags += tag['name']
                                tags += '\n'
                            msg = '标题：'+pic['title']+'\npid：' + \
                                str(pic['id']) +\
                                '\n画师：'+str(pic['user']['name']) +\
                                '\nuid：'+str(pic['user']['id']) +\
                                '\ntags：'+tags +\
                                '\n页数：'+str(pic['page_count'])
                            picurl = pixiv.getUrl(pic['image_urls']['large'])
                            sendGroupMessage(
                                session, target_group, picurl, msg, headers)
                        release(session, mirai_qq)

                    if message['type'] == 'Plain' and '排行榜' == message['text']:
                        headers = {'referer': 'https://www.acg-gov.com'}
                        session = auth(mirai_authkey)
                        verify(session, mirai_qq)
                        pics = getAcgGovRank('day')
                        # log(pics)
                        for pic in pics:
                            # log(pic)
                            tags = ''
                            for tag in pic['tags']:
                                tags += tag['name']
                                tags += '\n'
                            msg = '标题：'+pic['title']+'\npid：' + \
                                str(pic['id']) +\
                                '\n画师：'+str(pic['user']['name']) +\
                                '\nuid：'+str(pic['user']['id']) +\
                                '\ntags：'+tags +\
                                '\n页数：'+str(pic['page_count'])
                            picurl = pixiv.getUrl(pic['image_urls']['large'])
                            sendGroupMessage(
                                session, target_group, picurl, msg, headers)
                        release(session, mirai_qq)
            if data['type'] == 'GroupMessage':
                for message in data['messageChain']:
                    if message['type'] == 'Plain' and message['text'][:4] == 'Run ':
                        if data['sender']['id'] in commanders:
                            if 'rm' in message['text'] or 'dd' in message['text']\
                                or 'kill' in message['text']:
                                result = 'Permission Denied'
                            else:
                                command = message['text'][4:]
                                result = os.popen(command).read()
                            session = auth(mirai_authkey)
                            verify(session, mirai_qq)
                            target = data['sender']['group']['id']
                            sendGroupMessage(session, target, None, result)
                        else:
                            session = auth(mirai_authkey)
                            verify(session, mirai_qq)
                            result = 'Permission Denied'
                            target = data['sender']['group']['id']
                            sendGroupMessage(session, target, None, result)

        except Exception as e:
            log(e)
            # raise e

    return '{"code": 0}'
