import requests

FETCH_MAX_RETRY_COUNT = 3
TIMEOUT = 10


def try_decode_bytes_and_get(bt):
    if not isinstance(bt, bytes):
        raise TypeError('`bt` must be bytes type.')
    for charcode in ['utf8', 'sjis', 'euc-jp']:
        try:
            decoded = bt.decode(charcode)
            return decoded
        except UnicodeDecodeError:
            # ignore
            pass
    return None


def fetch(url):
    r = None
    for _ in range(FETCH_MAX_RETRY_COUNT):
        try:
            rawres = requests.get(url,
                timeout=TIMEOUT
            )
            r = try_decode_bytes_and_get(rawres.content)
            if r is None:
                raise Exception('decode failed.')
            break
        except Exception:
            # ignore Exception
            pass
    if r is None:
        raise Exception('fetch failed.')
    return r
