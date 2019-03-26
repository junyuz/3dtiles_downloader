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


def getContents(contents, n):
    #下载content url里的东西
    if 'content' in n:
        c = n['content']
        if 'url' in c:
            contents.append(c['url'])
        if 'uri' in c:
            contents.append(c['uri'])


    if 'children' in n:
        children = n['children']
        for i in range(len(children)):
            c = children[i]
            getContents(contents,c)
    return

def readContents(url,saveDir,name,contents):
    saveFile = saveDir + '/'+ name
    i,r = autoDownLoad(url+'/'+name,saveFile,0)
    if not r:
        sys.exit(2)
    tileset = None
    try:
        f = codecs.open(saveFile,'r','utf-8')
        s = f.read()
        f.close()

        tileset = json.loads(s)
    except Exception as e:
        print (e)

    getContents(contents,tileset['root'])
    for i in range(0,len(contents)):
        c = contents[i]
        if c.endswith('.json'):
            contents.remove(c)
            readContents(url,saveDir,c,contents)
        # else :
        #     file = savedir+'/' + c  
        #     dirname =  os.path.dirname(file)
        #     if not os.path.exists(dirname):
        #         os.makedirs(dirname)

        #     dUrl = url+'/'+c
        #     autoDownLoad(dUrl,file,i)


def autoDownLoad(url,saveFile,index):
    try:
        opener = request.build_opener()
        opener.addheaders = [
            ('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'),
            ('Accept','application/json,*/*;q=0.01,*/*;access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlMDZhZGY5My0wZTBkLTQxN2YtYjc4Yy1mNjliZjNlNjQwN2EiLCJpZCI6MjU5LCJhc3NldHMiOnsiMTY0MjEiOnsidHlwZSI6IjNEVElMRVMifX0sInNyYyI6ImUxZDdlYmVjLTVkMzUtNDY1Ny04NWExLTgyNDYwY2M5MGQ2NSIsImlhdCI6MTU1MzI0MDIwNywiZXhwIjoxNTUzMjQzODA3fQ.2vHRRovWy8KtrcvAv5pCp-YikMEpt11EpatHKst-0w4')]
        request.install_opener(opener)
        a, b = request.urlretrieve(url, saveFile)
        #a表示地址， b表示返回头
        keyMap = dict(b)
        if 'Content-Encoding' in keyMap and keyMap['Content-Encoding'] == 'gzip':
            with gzip.open(saveFile, 'rb') as g:
                text = g.read()
                objectFile = open(saveFile, 'rb+')#以读写模式打开
                objectFile.seek(0, 0)
                objectFile.write(text)
                objectFile.close()

        return index,True
  
    except request.ContentTooShortError:
        print ('Network conditions is not good.Reloading.')
        autoDownLoad(url,saveFile)
    except socket.timeout:
        print ('fetch ', url,' exceedTime ')
        try:
            urllib.urlretrieve(url,saveFile)
        except:
            print ('reload failed')
    except Exception:
        traceback.print_exc()


    return index,False

class DownloadThreadPool(object):
    '''
    启用最大并发线程数为5的线程池进行URL链接爬取及结果解析；
    最终通过crawl方法的complete_callback参数进行爬取解析结果回调
    '''
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=10)

    def _request_parse_runnable(self, url,file, index):
        return autoDownLoad(url,file,index)

    def autoDownLoad(self, url, file, index, complete_callback):
        future = self.thread_pool.submit(self._request_parse_runnable, url, file, index)
        future.add_done_callback(complete_callback)

class CrawlManager(object):
    '''
    爬虫管理类，负责管理线程池
    '''
    def __init__(self):
        self.download_pool = DownloadThreadPool()

    def _download_future_callback(self, download_url_future):
        try:
            index,result = download_url_future.result()
            if result:
                print  ('download success: ', index , '/' , self.len)
            else:
                print  ('download failed: ', index , '/' , self.len)
        except Exception as e:
            print('Run crawl url future thread error. '+str(e))

    def start_runner(self, url, file, index, len):
        self.len = len
        self.download_pool.autoDownLoad(url, file, index, self._download_future_callback)

if __name__ == "__main__":
    baseurl = 'http://data.marsgis.cn//3dtiles/max-jcz'
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

    contents = []
    readContents(baseurl,savedir,'tileset.json',contents)
    crawManager = CrawlManager()

    for i in range(start,len(contents)):
        c = contents[i]

        file = savedir+'/' + c

        dirname =  os.path.dirname(file)
        if not os.path.exists(dirname):
            os.makedirs(dirname) 

        url = baseurl + '/'+ c
        crawManager.start_runner(url, file, i, len(contents))