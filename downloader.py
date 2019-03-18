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


def getContents(contents, n):
    #下载content url里的东西
    if 'content' in n:
        c = n['content']
        if 'url' in c:
            contents.append(c['url'])


    if 'children' in n:
        children = n['children']
        for i in range(len(children)):
            c = children[i]
            getContents(contents,c)
    return

def autoDownLoad(url,add):
    try:
        opener = request.build_opener()
        opener.addheaders = [
            ('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'),
            ('Accept','application/json,*/*;q=0.01,*/*;access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlYzU5NTA1OS1mZDUxLTQ2YTgtYjQzMS1mMjA4YjBhMTMwMjciLCJpZCI6NDQsImFzc2V0cyI6eyIxNDYxIjp7InR5cGUiOiIzRFRJTEVTIn19LCJzcmMiOiJiMTBjN2E3Mi03ZGZkLTRhYmItOWEzNC1iOTdjODEzMzM5MzgiLCJpYXQiOjE1NTI4ODgyNTgsImV4cCI6MTU1Mjg5MTg1OH0.63RvcO1wXZhA44GYmmrXyJz_pH14jEvBVSNE6pQzS34')]
        request.install_opener(opener)
        a, b = request.urlretrieve(url, add)
        #a表示地址， b表示返回头
        keyMap = dict(b)
        if 'Content-Encoding' in keyMap and keyMap['Content-Encoding'] == 'gzip':
            with gzip.open(add, 'rb') as g:
                text = g.read()
                objectFile = open(add, 'rb+')#以读写模式打开
                objectFile.seek(0, 0)
                objectFile.write(text)
                objectFile.close()

        return True
  
    except request.ContentTooShortError:
        print ('Network conditions is not good.Reloading.')
        autoDownLoad(url,add)
    except socket.timeout:
        print ('fetch ', url,' exceedTime ')
        try:
            urllib.urlretrieve(url,add)
        except:
            print ('reload failed')
    except Exception:
        traceback.print_exc()


    return False

if __name__ == "__main__":
    baseurl = 'https://assets.cesium.com/1461/tileset.json?v=1'
    savedir = 'E:/3dtiles/ttt'
    start = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:d:s:", ["url=","dir=","start="])
    except getopt.GetoptError:
        print ('param error')
        sys.exit(2)


    for opt, arg in opts:
        if opt == '-h':
            print ('python downloader.py  url  dir')
            sys.exit()
        elif opt in ("-u", "--url"):
            baseurl = arg
        elif opt in ("-d", "--dir"):
            savedir = arg
        elif opt in ("-s", "--start"):
            start = int(arg)

    if baseurl == '':
        print ('please input url param')
        sys.exit(2)
    if savedir == '':
        print ('please input dir param')
        sys.exit(2)

    if os.path.isfile(savedir):
        print ('savedir can not be a file ',savedir)
        sys.exit(2)

    if not os.path.exists(savedir):
        os.makedirs(savedir)

    uu = parse.urlparse(baseurl)
    tileseturl = uu.scheme + "://" + uu.netloc  + uu.path
    if not tileseturl.endswith('tileset.json'):
        tileseturl +=  '/tileset.json'

    baseurl = tileseturl[0:tileseturl.find('tileset.json')]

    tilesetfile = savedir+'/tileset.json'
    if not autoDownLoad(tileseturl,tilesetfile):
        sys.exit(2)
    


    print ('download tileset.json success')

    #解析
    tileset = None
    try:
        f = codecs.open(tilesetfile,'r','utf-8')
        s = f.read()
        f.close()

        tileset = json.loads(s)
    except Exception as e:
        print (e)    

    contents = []
    getContents(contents,tileset['root'])


    for i in range(start,len(contents)):
        c = contents[i]

        file = savedir+'/' + c

        dirname =  os.path.dirname(file)
        if not os.path.exists(dirname):
            os.makedirs(dirname) 

        url = baseurl + c + '?' + uu.query
        if autoDownLoad(url,file):
            print  (c ,' download success: '  ,  str(i+1) , '/' , str(len(contents)))
        else:
            print  (c , ' download failed: '  , str(i+1) , '/' , str(len(contents)))
