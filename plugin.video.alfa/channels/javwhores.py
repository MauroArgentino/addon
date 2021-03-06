# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools


host = 'https://www.javbangers.com'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append( Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/latest-updates/"))
    itemlist.append( Item(channel=item.channel, title="Mejor valorados" , action="lista", url=host + "/top-rated/"))
    itemlist.append( Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "/most-popular/"))
    itemlist.append( Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/categories/"))
    itemlist.append( Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search/%s/" % (host, texto)
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
    patron  = '<a class="item" href="([^"]+)" title="([^"]+)">.*?'
    patron  += '<img class="thumb" src="([^"]+)".*?'
    patron  += '<div class="videos">([^"]+)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for scrapedurl,scrapedtitle,scrapedthumbnail,cantidad  in matches:
        title = "%s (%s)" %(scrapedtitle,cantidad)
        scrapedplot = ""
        itemlist.append( Item(channel=item.channel, action="lista", title=title, url=scrapedurl,
                              thumbnail=scrapedthumbnail , plot=scrapedplot) )
    return sorted(itemlist, key=lambda i: i.title)


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    # PURGA los PRIVATE 
    patron  = 'div class="video-item\s+".*?href="([^"]+)".*?'
    patron += 'data-original="([^"]+)" '
    patron += 'alt="([^"]+)"(.*?)fa fa-clock-o"></i>([^<]+)<'
    matches = scrapertools.find_multiple_matches(data, patron)
    for scrapedurl, scrapedthumbnail, scrapedtitle, quality, duration in matches:
        url = urlparse.urljoin(host, scrapedurl)
        scrapedtitle = scrapedtitle.strip()
        if not 'HD' in quality :
            title = "[COLOR yellow]%s[/COLOR] %s" % (duration.strip(), scrapedtitle)
        else:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (duration.strip(), scrapedtitle)
        thumbnail = scrapedthumbnail
        plot = ""
        itemlist.append( Item(channel=item.channel, action="play", title=title, url=url, thumbnail=thumbnail,
                              plot=plot, contentTitle = title))
    next_page = scrapertools.find_single_match(data, '<li class="next"><a href="([^"]+)"')
    if "#videos" in next_page:
        next_page = scrapertools.find_single_match(data, 'data-parameters="sort_by:post_date;from:(\d+)">Next')
        next = scrapertools.find_single_match(item.url, '(.*?/)\d+')
        next_page = next + "%s/" % next_page
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title= "Página Siguiente >>", text_color="blue", url=next_page ) )
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    if "video_url_text" in data:
        patron = '(?:video_url|video_alt_url[0-9]*):\s*\'([^\']+)\'.*?'
        patron += '(?:video_url_text|video_alt_url[0-9]*_text):\s*\'([^\']+)\''
    else:
        patron = '(?:video_url|video_alt_url[0-9]*):\s*\'([^\']+)\'.*?'
        patron += 'postfix:\s*\'([^\']+)\''
    matches = scrapertools.find_multiple_matches(data, patron)
    for url,quality in matches:
        itemlist.append(['%s' %quality, url])
    return itemlist


