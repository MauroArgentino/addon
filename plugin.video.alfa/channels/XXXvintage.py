# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from core import httptools

host = 'http://www.vintagetube.xxx'

def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Ultimos" , action="lista", url=host + "/latest/all-time/1"))
    itemlist.append( Item(channel=item.channel, title="Mas visto" , action="lista", url=host + "/most-viewed/all-time/1"))
    itemlist.append( Item(channel=item.channel, title="Pornstar" , action="categorias", url=host + "/models/top-rated/"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "%20")
    item.url = host + "/search/%s" % texto
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    if "Pornstar" in item.title:
        patron = '<a href="([^"]+)"><div style="display:inline"><img src="([^"]+)".*?'
        patron += '<strong class="thumb-title">([^<]+)<'
    else:
        patron  = '<li><a href="([^"]+)"><div style="(display:inline)">([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        scrapedplot = ""
        if not "Pornstar" in item.title:
            scrapedthumbnail = ""
            url = "%s%s/latest/1" % (host,scrapedurl)
        else:
            url = "%s%s" % (host,scrapedurl)
        itemlist.append( Item(channel=item.channel, action="lista", title=scrapedtitle, url=url,
                              thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot) )
    return sorted(itemlist, key=lambda i: i.title)


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron = '<div class="item col-lg-2 col-md-3 col-xs-12">.*?'
    patron += '<a href="([^"]+)">.*?'
    patron += '<span class="duration">([^<]+)</span>.*?'
    patron += 'src="([^"]+)".*?'
    patron += '<strong class="thumb-title">([^<]+)</strong>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtime,scrapedthumbnail,scrapedtitle in matches:
        scrapedplot = ""
        title = "[COLOR yellow]%s[/COLOR] %s" %(scrapedtime,scrapedtitle)
        scrapedurl = scrapedurl.replace("/xxx.php?tube=", "")
        scrapedurl = host + scrapedurl
        itemlist.append( Item(channel=item.channel, action="play", title=title, contentTitle=title, url=scrapedurl,
                              thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot) )
    last_page= scrapertools.find_single_match(data,'<a href=".*?/latest/(\d+)"><div style="display:inline">Last<')
    logger.debug(last_page)
    page = scrapertools.find_single_match(item.url, "(.*?)/\d+")
    current_page = scrapertools.find_single_match(item.url, ".*?/(\d+)")
    if last_page:
        last_page = int(last_page)
    if current_page:
        current_page = int(current_page)
    if current_page < last_page:
        current_page = current_page + 1
        next_page = "%s/%s" %(page,current_page)
        itemlist.append(Item(channel=item.channel, action="lista", title=next_page, text_color="blue",
                              url=next_page, thumbnail=""))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = 'mp4":{"link":"([^"]+)","w":"\d+","h":"(\d+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for url,quality in matches:
        itemlist.append(['.mp4 %s' %quality, url])
    return itemlist

