from mkp import settings
from mkp import utanet
from mkp import data
from mkp.logging import getLogger
import os
import datetime

import pickle

with open('storage/artists.pickle', 'rb') as f:
    artist_ids = pickle.load(f)


logger = getLogger(__name__)

def main():
    cnt = 0
    for aid in artist_ids.keys():
        logger.info('cnt: {} .. start'.format(cnt))
        with data.connection_scope(ro=True) as conn:
            cur = conn.cursor()
            cur.execute('select id from artists')
            r = cur.fetchall()
        if len(r) == 0:
            with data.connection_scope() as conn:
                cur = conn.cursor()
                cur.execute('insert into artists values (?,?,?)', (aid, artist_ids[aid], datetime.datetime.now(),))
        musics = utanet.list_musics_by_artistid(aid)
        for music in musics:
            logger.debug(
                '===== kid: {}, titlename: {}, words_artistname: {}, music_artistname: {} .. start.'.format(
                    music['id'], music['titlename'], music['words_artistname'], music['music_artistname']
                ))
            kasi = utanet.get_kasi_by_kasiid(music['id'])

            # save
            data.save_kasi(music['id'], aid, music['titlename'], music['words_artistname'], music['music_artistname'])
            data.save_kasi_file(kasi, music['id'])
            logger.debug(
                '===== kid: {}, titlename: {}, words_artistname: {}, music_artistname: {} .. done.'.format(
                    music['id'], music['titlename'], music['words_artistname'], music['music_artistname']
                ))
        logger.info('cnt: {} .. done'.format(cnt))
        cnt += 1


if __name__ == '__main__':
    main()
