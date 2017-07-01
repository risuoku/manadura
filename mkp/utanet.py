from . import crawler
from bs4 import BeautifulSoup
import re

def list_musics_by_artistid(aid):
    r = crawler.fetch('http://www.uta-net.com/artist/{}/'.format(aid))
    results = []
    bso = BeautifulSoup(r, 'lxml')
    result_tables = bso.select('.result_table')

    for rt in result_tables:
        mitems = rt.select_one('table').select_one('tbody').select('tr')
        for mitem in mitems:
            titlename = mitem.select_one('td.side.td1').select_one('a').text
            kasi_regexp = re.search('^/song/([0-9]+)/$', mitem.select_one('td.side.td1').select_one('a')['href'])
            kasi_id = kasi_regexp.group(1)
            #artistname = mitem.select_one('td.td2').select_one('a').text
            words_artistname = mitem.select_one('td.td3').text
            music_artistname = mitem.select_one('td.td4').text
            results.append({
                'id': kasi_id,
                'artist_id': aid,
                'titlename': titlename,
                'words_artistname': words_artistname,
                'music_artistname': music_artistname,
            })
    return results


def get_kasi_by_kasiid(kid):
    def _convert_text(t):
        return re.sub('\u3000', ' ', t)

    a = crawler.fetch('http://www.uta-net.com/song/{}/'.format(kid))
    bso1 = BeautifulSoup(a, 'lxml')
    target1 = bso1.select_one('#ipad_kashi').select_one('img')
    b = crawler.fetch('http://www.uta-net.com' + target1['src'])
    bso2 = BeautifulSoup(b, 'lxml')
    texts = [
        _convert_text(t.text)
        for t in bso2.select_one('svg').select('text')
        if not t.text == ''
    ]
    return texts


def list_top100_artists():
    result = {}

    raw1 = crawler.fetch('http://www.uta-net.com/user/artist_ranking_100/2016/ranking_100_top.html')
    bso1 = BeautifulSoup(raw1, 'lxml')
    r1 = bso1.select_one('td[height="1693"]').select('table[width="231"]')
    for t in r1:
        tr = t.select('tr')
        atag = tr[0].select_one('a')
        gname_c = tr[2].select('td')[1].select_one('span')
        aid = re.search('http://www.uta-net.com/artist/([0-9]+)/?', atag['href']).group(1)
        aname = re.sub('\n', '', gname_c.text)
        result[aid] = aname
    r2 = bso1.select_one('#main').select_one('div[align="center"]').select_one('table').select_one('table').select_one('tr').select('td')
    for t in r2:
        for tt in t.select('table'):
            tr = tt.select('tr')
            atag = tr[0].select_one('a')
            gname_c = tr[2].select('td')[1].select_one('span')
            if gname_c is None: # 静的ファイルなのかspanついてないことがある...orz
                gname_c = tr[2].select('td')[1]
            aid = re.search('http://www.uta-net.com/artist/([0-9]+)/?', atag['href']).group(1)
            aname = re.sub('\n', '', gname_c.text)
            result[aid] = aname

    raw2 = crawler.fetch('http://www.uta-net.com/user/artist_ranking_100/2016/ranking_100_2.html')
    bso2 = BeautifulSoup(raw2, 'lxml')
    r3 = bso2.select_one('#main').select('table')[1].select_one('td').select('table')[1].select_one('table').select('td')
    for t in r3:
        for tt in t.select('table[width="231"]'):
            tr = tt.select('tr')
            atag = tr[0].select_one('a')
            gname_c = tr[2].select('td')[1].select_one('span')
            if gname_c is None: # 静的ファイルなのかspanついてないことがある...orz
                gname_c = tr[2].select('td')[1]
            aid = re.search('http://www.uta-net.com/artist/([0-9]+)/?', atag['href']).group(1)
            aname = re.sub('\n', '', gname_c.text)
            result[aid] = aname

    return result
