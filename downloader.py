import codecs
import getopt
import gzip
import json
import os
import socket
import sys
import traceback
import urllib
from io import StringIO
from urllib import parse, request
from concurrent.futures import ThreadPoolExecutor


def getContents(contents, n, remotedir, query):
    # 下载content url里的东西
    if 'content' in n:
        c = n['content']
        if 'url' in c:
            contents.append(
                remotedir + '/' + c['url'] + ("" if query is None else ('?' + query)))
        if 'uri' in c:
            contents.append(
                remotedir + '/'+c['uri'] + ("" if query is None else ('?' + query)))

    if 'children' in n:
        children = n['children']
        for i in range(len(children)):
            c = children[i]
            getContents(contents, c, remotedir, query)
    return


def readContents(url, saveDir, contents, token):
    urlp = urllib.parse.urlparse(url)
    saveFile = saveDir + urlp.path
    remotedir, _ = os.path.split(url)
    i, r = autoDownLoad(url, saveFile, 0, token)
    if not r:
        sys.exit(2)
    tileset = None
    try:
        f = codecs.open(saveFile, 'r', 'utf-8')
        s = f.read()
        f.close()

        tileset = json.loads(s)
    except Exception as e:
        print(e)

    getContents(contents, tileset['root'], remotedir, urlp.query)
    for i in range(0, len(contents)):
        c = contents[i]
        if c.endswith('.json'):
            contents.remove(c)
            readContents(c, saveDir, contents, token)


def autoDownLoad(url, saveFile, index, token):
    try:
        opener = request.build_opener()
        opener.addheaders = [
            ('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'),
            ('Accept', 'application/json,*/*;q=0.01,*/*;')]
        if token is not None:
            opener.addheaders.append(('Authorization', 'Bearer ' + token))
        request.install_opener(opener)

        savedir, _ = os.path.split(saveFile)
        os.makedirs(savedir, exist_ok=True)

        a, b = request.urlretrieve(url, saveFile)
        # a表示地址， b表示返回头
        keyMap = dict(b)
        if 'Content-Encoding' in keyMap and keyMap['Content-Encoding'] == 'gzip':
            with gzip.open(saveFile, 'rb') as g:
                text = g.read()
                objectFile = open(saveFile, 'rb+')  # 以读写模式打开
                objectFile.seek(0, 0)
                objectFile.write(text)
                objectFile.close()

        return index, True

    except request.ContentTooShortError:
        print('Network conditions is not good.Reloading.')
        autoDownLoad(url, saveFile, index, token)
    except socket.timeout:
        print('fetch ', url, ' exceedTime ')
        try:
            urllib.urlretrieve(url, saveFile)
        except:
            print('reload failed')
    except Exception:
        traceback.print_exc()

    return index, False


def ion_authorize(asset_id):
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlNzMyOGZjZC1jMWUzLTQxNDctOGQxYi03YTYyZDQ1OTIxMjkiLCJpZCI6MjU5LCJpYXQiOjE2MDE1Njk1NDN9.X1a0DCM6F539g9MDSs_ldZ0gwgruxLAZiBl60JwG1ck"
    endpoint_base_url = "https://api.cesium.com/v1/assets/"

    endpoint_respond = urllib.request.urlopen(endpoint_base_url +
                                              str(asset_id) + "/endpoint?access_token=" + access_token)
    endpoint_respond = json.loads(endpoint_respond.read())
    return endpoint_respond


if __name__ == "__main__":

    # 下载参数设置
    asset_id = 40866
    savedir = 'C:/3dtiles_donwloader'
    start = 0

    if os.path.isfile(savedir):
        print('savedir can not be a file ', savedir)
        sys.exit(2)

    os.makedirs(savedir, exist_ok=True)

    endpoint = ion_authorize(40866)

    contents = []
    readContents(endpoint['url'], savedir, contents, endpoint['accessToken'])

    for i in range(start, len(contents)):
        c = contents[i]

        urlp = urllib.parse.urlparse(c)
        file = savedir + '/' + urlp.path

        dirname = os.path.dirname(file)
        os.makedirs(dirname, exist_ok=True)

        print('downloading', c, str(i+1) + '/' + str(len(contents)))
        autoDownLoad(c, file, i, endpoint['accessToken'])

    print('done.')
