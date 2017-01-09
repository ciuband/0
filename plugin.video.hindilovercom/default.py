import os
import re
import sys
import urllib
import urllib2
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

if not xbmc.getCondVisibility('System.HasAddon(script.module.urlresolver)'):
    xbmc.executebuiltin('XBMC.RunPlugin(plugin://script.module.urlresolver)')
    
try:
    import urlresolver
except:
    pass

settings = xbmcaddon.Addon(id='plugin.video.hindilovercom')

search_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'search.png')
movies_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'movies.png')
next_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'next.png')
base_url = 'http://hindilover.net'

def ROOT():
    addDir('Recente', base_url + '/news/', 6, movies_thumb, 'recente')
    addDir('Filme Indiene', base_url + '/news/1-0-31', 6, movies_thumb, 'recente')
    addDir('Seriale Indiene Terminate', base_url, 6, movies_thumb, 'SerialIT')
    addDir('Seriale Indiene in desfasurare', base_url + '/index/0-53', 6, movies_thumb, 'SerialT')
    addDir('Seriale Turcesti', base_url + '/index/0-54', 6, movies_thumb, 'SerialT') #
    addDir('Desene Animate', base_url + '/news/1-0-35', 6, movies_thumb, 'recente')
    addDir('Cauta', base_url, 3, search_thumb)
    
def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def CAUTA_LIST(url):
    link = get_search(url)
                   
    regex_menu = '''<div class="eTitle"(.+?)</div></td></tr></table><br />'''
    regex_submenu = '''<a href="(.+?)".+?>(.+?)</a>'''
    for meniu in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
        match = re.compile(regex_submenu, re.DOTALL).findall(meniu)
        for legatura, nume in match:
            addDir(nume, legatura, 5, movies_thumb)

    match = re.compile('"swchItem"', re.IGNORECASE).findall(link)
    if len(match) > 0:
        new = re.compile('/\?q=.+?t=\d+;p=(\d+);md').findall(url)
        if new:
            nexturl = re.sub('p=\d+', 'p=' + (str(int(new[0]) + 1)), url)
        else:
            nexturl = url + ';t=0;p=2;md='
      
        print "NEXT " + nexturl
      
        addNext('Next', nexturl, 5, next_thumb)
            
 
def CAUTA_VIDEO_LIST(url):
    link = get_search(url)
    regex_src = '''<div id="Server_\d+"(.+?)</div>'''
    regex_lnk = '''(?:a href=|src=)"(.+?)"'''
    for meniu in re.compile(regex_src, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
        match = re.compile(regex_lnk, re.DOTALL).findall(meniu)
        for link1 in match:
            if link1.startswith("//"):
                link1 = 'http:' + link1 #//ok.ru fix
            parsed_url1 = urlparse.urlparse(link1)
            if parsed_url1.scheme:
                hmf = urlresolver.HostedMediaFile(url=link1, include_disabled=True, include_universal=True)
                if hmf.valid_url() == True:
                    host = link1.split('/')[2].replace('www.', '').capitalize()
                    sxaddLink(host, link1, movies_thumb, link1, 10)

            

def CAUTA(url, autoSearch=None):
    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed() == False):
        return
    search_string = keyboard.getText()
    if len(search_string) == 0:
        return
        
    if autoSearch is None:
        autoSearch = ""
    
    CAUTA_LIST(get_search_url(search_string + "" + autoSearch))
    
def SXVIDEO_GENERIC_PLAY(sxurl):
    #stream_url = urlresolver.resolve(url)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=movies_thumb); liz.setInfo(type="Video", infoLabels={"Title": name})
    hmf = urlresolver.HostedMediaFile(url=sxurl, include_disabled=True, include_universal=False)
    xbmc.Player ().play(hmf.resolve(), liz, False)
    
def get_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    try:
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        return link
    except:
        return False
    
def get_search_url(keyword, offset=None):
    url = base_url + '/search/?q=' + urllib.quote_plus(keyword)
    
    if offset != None:
        url += "?offset=" + offset
    
    return url
  
def get_search(url):
    
    params = {}
    req = urllib2.Request(url, urllib.urlencode(params))
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_header('Content-type', 'application/x-www-form-urlencoded')
    try:
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        return link
    except:
        return False

def parse_menu(url, meniu):
    match = []
    if url == None:
        url = base_url
    link = get_url(url)
    if meniu == 'recente':
        regex_menu = '''<div class="eTitle"(.+?)</div></td></tr></table><br />'''
        regex_submenu = '''<a href="(.+?)".+?>(.+?)</a>.+?<img src="(.+?)"'''
        for meniu in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
            match = re.compile(regex_submenu, re.DOTALL).findall(meniu)
            for legatura, nume, imagine in match:
                nume = striphtml(nume)
                link_fix = base_url + legatura
                addDir(nume, link_fix, 5, imagine)
        match = re.compile('"swchItem"', re.IGNORECASE).findall(link)
        if len(match) > 0:
            new = re.compile('/(\d+)').findall(url)
            if new:
                nexturl = re.sub('/(\d+)', '/' + str(int(new[0]) + 1), url)
                print "NEXT " + nexturl
                addNext('Next', nexturl, 6, next_thumb, 'recente')
            else:
                new = re.compile('/\?page(\d+)').findall(url)
                if new:
                    nexturl = re.sub('page\d+', 'page' + (str(int(new[0]) + 1)), url)
                else:
                    nexturl = url + '?page2'
                addNext('Next', nexturl, 6, next_thumb, 'recente')
    elif meniu == 'SerialT':
        match = re.compile('class="catsTdI".+?a href="(.+?)".+?class="abcdD.+?>(.+?)<', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
        if len(match) > 0:
            for legatura, nume in match:
                nume = striphtml(nume)
                addDir(nume, legatura, 6, movies_thumb, 'recente')
    elif meniu == 'SerialIT':
        regex_menu = '''<nav class="nav">.+?Indiene(.+?)</ul>'''
        regex_submenu = '''href="(.+?)">(.+?)<.+?'''
        for meniu in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
            match = re.compile(regex_submenu, re.DOTALL).findall(meniu)
            for legatura, nume in match:
                nume = striphtml(nume)
                addDir(nume, legatura, 6, movies_thumb, 'recente')

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params)-1] == '/'):
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
                                
    return param

def sxaddLink(name, url, iconimage, movie_name, mode=4):
    ok = True
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": movie_name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok

def addNext(name, page, mode, iconimage, meniu=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(page) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    if meniu != None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addDir(name, url, mode, iconimage, meniu=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    if meniu != None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok
              
params = get_params()
url = None
name = None
mode = None

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    name = urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass
try:
    meniu = urllib.unquote_plus(params["meniu"])
except:
    pass
#print "Mode: "+str(mode)
#print "URL: "+str(url)
#print "Name: "+str(name)

if mode == None or url == None or len(url) < 1:
    ROOT()
        
elif mode == 2:
    CAUTA_LIST(url)
        
elif mode == 3:
    CAUTA(url)
        
elif mode == 5:
    CAUTA_VIDEO_LIST(url)
        
elif mode == 6:
    parse_menu(url, meniu)

elif mode == 4:
    VIDEO(url, name)

elif mode == 10:
    SXVIDEO_GENERIC_PLAY(url)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
