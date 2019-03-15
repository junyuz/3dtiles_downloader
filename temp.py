import getopt
import gzip
from io import StringIO
import os
import socket
import sys
import traceback
import urllib
from urllib import request


def gzdecode(data):  
    #compressedStream = StringIO(data)  
    #gziper = gzip.GzipFile(fileobj=compressedStream)
    buf = StringIO(data)
    gziper = gzip.GzipFile(fileobj=buf)    
    data2 = gziper.read()  
    return data2 

def autoDownLoad(url,add):
    try:
        opener = request.build_opener()
        opener.addheaders = [
            ('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'),
            ('Accept','application/json,*/*;q=0.01,*/*;access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJiZTQwYzRmZC1hZWY4LTQ1MGQtOTBlZC00M2ViNzUwMzMzNGYiLCJpZCI6NDQsImFzc2V0cyI6eyIxNDYxIjp7InR5cGUiOiIzRFRJTEVTIn19LCJzcmMiOiJiMTBjN2E3Mi03ZGZkLTRhYmItOWEzNC1iOTdjODEzMzM5MzgiLCJpYXQiOjE1NTI2MzkxNjMsImV4cCI6MTU1MjY0Mjc2M30.ynJTQoI7jUSjtlucC_c0-A46FVHRBC6Nmi5XkbHKEj0')]
        request.install_opener(opener)
        a, b = request.urlretrieve(url, add)
        #a表示地址， b表示返回头
        keyMap = dict(b)
        if 'Content-Encoding' in keyMap and keyMap['Content-Encoding'] == 'gzip':
            with gzip.open(add, 'rb') as g:
                text = g.read()
                with gzip.open(add, 'wb') as f:
                    f.write(text)

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

    tilesetfile = savedir+'/tileset.json'
    if not autoDownLoad(baseurl,tilesetfile):
        sys.exit(2)
    


    print ('download tileset.json success')
