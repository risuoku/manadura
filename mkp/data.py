import importlib
import os
import sqlite3
import datetime
import binascii
from contextlib import contextmanager

from . import settings


self = importlib.import_module(__name__)

_setup_done = False


def setup():
    conn = sqlite3.connect(os.path.join(settings.STORAGE_DIR, settings.DB_NAME))
    cur = conn.cursor()
    cur.execute("""\
    create table if not exists kasi(\
    id varchar(32) primary key, \
    artist_id varchar(32), \
    titlename varchar(255), \
    words_artistname varchar(255), \
    music_artistname varchar(255), \
    created_at datetime\
    )""")
    cur.execute("""\
    create table if not exists artists(\
    id varchar(32) primary key, \
    name varchar(255), \
    created_at datetime\
    )""")
    conn.commit()
    conn.close()
    self._setup_done = True


def _check_setup_done():
    if not self._setup_done:
        raise ValueError('setup not done.')


@contextmanager
def connection_scope(ro = False):
    _check_setup_done()
    conn = sqlite3.connect(os.path.join(settings.STORAGE_DIR, settings.DB_NAME))
    try:
        yield conn
        if not ro:
            conn.commit()
    except:
        if not ro:
            conn.rollback()
        raise
    finally:
        conn.close()


def save_kasi(kid, artist_id, titlename, words_artistname, music_artistname):
    with connection_scope() as conn:
        cur = conn.cursor()
        cur.execute('insert into kasi values (?,?,?,?,?,?)',
            (kid, artist_id, titlename, words_artistname, music_artistname, datetime.datetime.now()))


def _resolve_filepath_by_id(kid):
    kid = str(kid)
    pid = binascii.crc32(kid.encode('utf8'))%100
    targetdir = os.path.join(settings.STORAGE_DIR, str(pid))
    if not os.path.isdir(targetdir):
        os.makedirs(targetdir)
    return os.path.join(targetdir, '{}.txt'.format(kid))


def load_kasi_file(kid):
    fpath = _resolve_filepath_by_id(kid)
    r = None
    with open(fpath) as f:
        r = f.readlines()
    return r


def save_kasi_file(strlist, kid):
    fpath = _resolve_filepath_by_id(kid)
    with open(fpath, 'w') as f:
        f.write('\n'.join(strlist))
