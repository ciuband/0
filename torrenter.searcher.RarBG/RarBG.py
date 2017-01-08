# -*- coding: utf-8 -*-
'''
    Torrenter v2 plugin for XBMC/Kodi
    Copyright (C) 2012-2015 Vadim Skorba v1 - DiMartino v2
    http://forum.kodi.tv/showthread.php?tid=214366

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import SearcherABC
import json
import os
import socket
import sys
import urllib
import urllib2
import xbmcaddon


class RarBG(SearcherABC.SearcherABC):

    __torrenter_settings__ = xbmcaddon.Addon(id='plugin.video.torrenter')
    #__torrenter_language__ = __settings__.getLocalizedString
    #__torrenter_root__ = __torrenter_settings__.getAddonInfo('path')

    ROOT_PATH = os.path.dirname(__file__)
    addon_id = ROOT_PATH.replace('\\', '/').rstrip('/').split('/')[-1]
    __settings__ = xbmcaddon.Addon(id=addon_id)
    __addonpath__ = __settings__.getAddonInfo('path')
    __version__ = __settings__.getAddonInfo('version')
    __plugin__ = __settings__.getAddonInfo('name') + " v." + __version__

    baseurl = 'http://torrentapi.org/pubapi_v2.php'
    '''
    Setting the timeout
    '''
    torrenter_timeout_multi = int(sys.modules["__main__"].__settings__.getSetting("timeout"))
    timeout_multi = int(__settings__.getSetting("timeout"))

    '''
    Weight of source with this searcher provided. Will be multiplied on default weight.
    '''
    sourceWeight = 1

    '''
    Full path to image will shown as source image at result listing
    '''
    searchIcon = os.path.join(__addonpath__, 'icon.png')

    '''
    Flag indicates is this source - magnet links source or not.
    '''

    @property
    def isMagnetLinkSource(self):
        return True

    '''
    Main method should be implemented for search process.
    Receives keyword and have to return dictionary of proper tuples:
    filesList.append((
        int(weight),# Calculated global weight of sources
        int(seeds),# Seeds count
        int(leechers),# Leechers count
        str(size),# Full torrent's content size (e.g. 3.04 GB)
        str(title),# Title (will be shown)
        str(link),# Link to the torrent/magnet
        str(image),# Path to image shown at the list
    ))
    '''


    def __init__(self):

        if self.timeout_multi == 0:
            socket.setdefaulttimeout(10 + (10 * self.torrenter_timeout_multi))
        else:
            socket.setdefaulttimeout(10 + (10 * (self.timeout_multi-1)))


        #self.debug = self.log


    def search(self, keyword):
        filesList = []
        sort = '&sort=seeders'
        if self.__settings__.getSetting('sortby') == '0':
            sort = '&sort=seeders'
	elif self.__settings__.getSetting('sortby') == '1':
            sort = '&sort=leechers'
	elif self.__settings__.getSetting('sortby') == '2':
            sort = '&sort=last'
        token = json.loads(get_data('%s?get_token=get_token&app_id=torrenter.searcher.RarBG' % (
                           self.baseurl)))
        search_url = "%s?mode=search&search_string=%s&app_id=torrenter.searcher.RarBG&format=json_extended&ranked=0%s&token=%s" % (
                                                                                                                                   self.baseurl, urllib.quote_plus(keyword), sort, token["token"])
        response = json.loads(get_data(search_url))
        if not response.has_key("error"):
            for info in response["torrent_results"]:
                link = info["download"]
                title = info["title"]
                seeds = info["seeders"]
                leechers = info["leechers"]
                size = get_size(info["size"])
                filesList.append((
                                 int(int(self.sourceWeight) * int(seeds)),
                                 int(seeds), int(leechers), size,
                                 title,
                                 self.__class__.__name__ + '::' + link,
                                 self.searchIcon,
                                 ))
        return filesList

def get_data(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/39.0.2171.71 Safari/537.36')
    req.add_header('Content-Language', 'en')
    opener = urllib2.build_opener()
    response = opener.open(req)
    content = response.read()
    response.close()
    return content

def get_size(bytes):
    alternative = [
        (1024 ** 5, ' PB'),
        (1024 ** 4, ' TB'), 
        (1024 ** 3, ' GB'), 
        (1024 ** 2, ' MB'), 
        (1024 ** 1, ' KB'),
        (1024 ** 0, (' byte', ' bytes')),
        ]
    for factor, suffix in alternative:
        if bytes >= factor:
            break
    amount = int(bytes / factor)
    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix
