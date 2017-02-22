# -*- coding: UTF-8 -*-
# by Mafarricos
# email: MafaStudios@gmail.com
# This program is free software: GNU General Public License

import re,threading,xbmcgui
import basic,tmdb,omdbapi
from BeautifulSoup import BeautifulSoup
from resources.libs import links
import datetime

def listmovies(url, tip):
	basic.log(u"cnmg.listmovies url: %s" % url)
	mainlist = []
	sendlist = [] 
	result = []
	threads = []
	order = 0
	htmlpage = basic.open_url(url)
	if tip == 'liste':
            regex = '''<li class="list_item clearfix">(.+?)</li>'''
            regex2 = '''<a [^>]*href\s*=\s*"[^"]*imdb.com/title/(.*?)/"'''
            for lists in re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(htmlpage):
                for imdb_id in re.compile(regex2, re.DOTALL).findall(lists):
                    order += 1
                    sendlist.append([order,imdb_id])
            target = tmdb.searchmovielist
        elif tip == 'filme':
            regex = '''<div class="poza">(.+?)</div>\n</li>'''
            regex2 = '''img src="(.+?)".+?<h2>.+?title.+?>(.+?)<.+?\((\d+)\).*(?:^$|<li>(.+?)</li>).*(?:^$|<li>(.+?)</li>).+?Gen.+?">(.+?)</ul>.+?(?:^$|\((.+?)\)).+?body".+?(?:^$|<span>(.+?)</span>)'''
            for lists in re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(htmlpage):
                for imagine,nume,an,regia,actori,gen,nota,descriere in re.compile(regex2, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(lists):
                    order += 1
                    nume = nume.decode('utf-8')
                    sendlist.append([order,imagine,nume,an,regia,actori,gen,nota,descriere])
            target = omdbapi.searchmovielist
	chunks=[sendlist[x:x+5] for x in xrange(0, len(sendlist), 5)]
	for i in range(len(chunks)): threads.append(threading.Thread(name='listmovies'+str(i),target=target,args=(chunks[i],result, )))
	[i.start() for i in threads]
	[i.join() for i in threads]
	result = sorted(result, key=basic.getKey)
	for id,lists in result: mainlist.append(lists)
	basic.log(u"imdb.listmovies mainlist: %s" % mainlist)
	return mainlist

def getgenre(url):
	genrechoice = xbmcgui.Dialog().select
	htmlpage = basic.open_url(url)	
	found = re.findall('<h3>Popular Movies by Genre</h3>.+?</html>',htmlpage, re.DOTALL)
	newfound = re.findall('<a href="/genre/(.+?)\?',found[0], re.DOTALL)
	choose=genrechoice("select",newfound)
	if choose > -1:	return newfound[choose]

def getyear():
        now_year = datetime.datetime.now().year
        year = []
        while (now_year > 1920):
            year.append(str(now_year))
            now_year -= 1
	yearchoice = xbmcgui.Dialog().select
	choose=yearchoice("select",year)
	if choose > -1:	return year[choose]

def getyearbygenre():
        genre = getgenre(links.link().imdb_genre)
        year = getyear(links.link().imdb_year)
	if genre and year: return genre, year

def striphtml(data):
    p = re.compile(r'<.*?>')
    p = p.sub('', data)
    p = " ".join(p.split())
    return p.strip()

def getliste(url):
        htmlpage = basic.open_url(url)
        liste = []
        order = 0
        regex = '''<div class="list_preview clearfix">(.+?)<div class="list_meta">(.+?)</div>'''
        regex2 = '''img src="(.+?)".+?list_name.+?<a href="(.+?)">(.+?)</a>'''
        #with open('/root/.kodi/temp/files.py', 'wb') as f: f.write(repr(htmlpage))
        for lists in re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(htmlpage):
            for imagine, link, nume in re.compile(regex2, re.DOTALL).findall(lists[0]):
                order += 1
                nume = nume.decode('utf-8')
                descriere = {'plot': (striphtml(lists[1]).strip()).decode('utf-8')}
                liste.append([order, imagine, link, nume, descriere])
        return liste

def gettari(url, tip=''):
        htmlpage = basic.open_url(url)
        tarisoara = []
        order = 0
        regex = '''class="filters_list">(.+?)</div'''
        regex2 = '''<a href="(.+?)".+?>(.+?)<'''
        tari = re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(htmlpage)
        if tip == 'tari': search = tari[2]
        elif tip == 'gen': search = tari[0]
        for link, nume in re.compile(regex2, re.DOTALL).findall(search):
            order += 1
            nume = nume.decode('utf-8')
            tarisoara.append([order, link, nume])
        return tarisoara

def getlinks(url,results,order,Source=None):
	basic.log(u"cnmg.getlinks url: %s" % url)
	try:
		html_page = basic.open_url(url)
		if html_page:
			soup = BeautifulSoup(html_page)
			if Source == 'cnmg':
				for link in soup.findAll('a', attrs={'href': re.compile("^/title/.+?/\?ref_=.+?_ov_tt")}):
					if '?' in link.get('href'): cleanlink = link.get('href').split("?")[0].split("title")[1].replace('/','').replace('awards','').replace('videogallery','')
					else: cleanlink = link.get('href').split("title")[1].replace('/','').replace('awards','').replace('videogallery','')
					results.append([order, cleanlink])
					order += 1			
			else:
				for link in soup.findAll('a', attrs={'href': re.compile("^http://.+?/title/")}):
					if '?' in link.get('href'): cleanlink = link.get('href').split("?")[0].split("/title/")[1].replace('/','').replace('awards','').replace('videogallery','')
					else: cleanlink = link.get('href').split("title")[1].replace('/','').replace('awards','').replace('videogallery','')
					results.append([order, cleanlink])
					order += 1
			basic.log(u"imdb.getlinks results: %s" % results)
			return results
	except BaseException as e: basic.log(u"imdb.getlinks ERROR: %s - %s" % (str(url),str(e)))
