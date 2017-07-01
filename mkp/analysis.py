import re
import os
import pickle
import MeCab
from sklearn.feature_extraction.text import TfidfVectorizer

from .data import (
    connection_scope,
    load_kasi_file,
)
from . import settings

tagger = MeCab.Tagger('-d /usr/lib/mecab/dic/mecab-ipadic-neologd')


def get_raw_list(_in):
    raw = tagger.parse(re.sub(',', '', _in))
    r2 = re.sub('\t', ',', raw)
    r_list = [tuple(a.split(',')) for a in r2.split('\n') if a not in ('', 'EOS',)]
    return r_list


def get_valid_word_list(artist_id, wordtype='verb'):
    with connection_scope(ro=True) as conn:
        cur = conn.cursor()
        cur.execute('select id from kasi where artist_id=?;', (artist_id,))
        r = cur.fetchall()
    idlist = [i for i, in r]

    if not wordtype in ('noun', 'verb',):
        raise ValueError('invalid wordtype.')

    if wordtype == 'verb':
        def _wfilter(s):
            return s[1] == '動詞' and s[2] == '自立'
    else:
        def _wfilter(s):
            return s[1] == '名詞'

    result = []
    for kid in idlist:
        #with open('{}.txt'.format(os.path.join(settings.STORAGE_DIR, kid))) as f:
        #    texts = f.readlines()
        texts = load_kasi_file(kid)
        tbuf = []
        for text in texts:
            tbuf += [r[0] for r in get_raw_list(text) if _wfilter(r)]
        result += list(set(tbuf)) # 同じ曲の中でのwordはuniqueにする
    return result


def noun_tokenizer(s):
    return [re.sub('っ', '', t[0]) for t in get_raw_list(s) if t[1] == '名詞']


def _convert_for_vt(s):
    #o = list(re.sub('っ', '', s[0]))
    o = list(re.sub('っ', '', s[8]))
    if len(o) > 2:
        return ''.join(o[:3])
    elif len(o) == 2:
        return ''.join(o[:2])
    else:
        return o[0]
def verb_tokenizer(s):
    return [
        _convert_for_vt(t)
        for t in get_raw_list(s)
        if t[1] == '動詞' and t[2] == '自立'
    ]


def get_document_by_aid(aid):
    with connection_scope(ro=True) as conn:
        cur = conn.cursor()
        cur.execute('select id from kasi where artist_id=?;', (aid,))
        r = cur.fetchall()
    idlist = [i for i, in r]
    result = []
    for kid in idlist:
        texts = load_kasi_file(kid)
        result += texts
    result = list(set(result))
    return ' '.join(result)


def get_sentences_by_aid(aid):
    with connection_scope(ro=True) as conn:
        cur = conn.cursor()
        cur.execute('select id from kasi where artist_id=?;', (aid,))
        r = cur.fetchall()
    idlist = [i for i, in r]
    result = []
    for kid in idlist:
        texts = load_kasi_file(kid)
        result += texts
    return result


stopwords = ['あ', 'い', 'う', 'え', 'お', 'か', 'き', 'く', 'け', 'こ', 'さ', 'し', 'す', 'せ', 'そ', 'た', 'ち', 'つ', 'て', 'と', 'な', 'に', 'ぬ', 'ね', 'の', 'は', 'ひ', 'ふ', 'へ', 'ほ', 'ま', 'み', 'む', 'め', 'も', 'や', 'ゆ', 'よ', 'ら', 'り', 'る', 'れ', 'ろ', 'わ', 'を', 'ん', 'が', 'ぎ', 'ぐ', 'げ', 'ご', 'ざ', 'じ', 'ず', 'ぜ', 'ぞ', 'だ', 'ぢ', 'づ', 'で', 'ど', 'ば', 'び', 'ぶ', 'べ', 'ぼ', 'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ', 'ア', 'イ', 'ウ', 'エ', 'オ', 'カ', 'キ', 'ク', 'ケ', 'コ', 'サ', 'シ', 'ス', 'セ', 'ソ', 'タ', 'チ', 'ツ', 'テ', 'ト', 'ナ', 'ニ', 'ヌ', 'ネ', 'ノ', 'ハ', 'ヒ', 'フ', 'ヘ', 'ホ', 'マ', 'ミ', 'ム', 'メ', 'モ', 'ヤ', 'ユ', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ワ', 'ヲ', 'ン', 'ガ', 'ギ', 'グ', 'ゲ', 'ゴ', 'ザ', 'ジ', 'ズ', 'ゼ', 'ゾ', 'ダ', 'ヂ', 'ヅ', 'デ', 'ド', 'バ', 'ビ', 'ブ', 'ベ', 'ボ', 'パ', 'ピ', 'プ', 'ペ', 'ポ']


def list_tfidf_scores():
    with open(os.path.join(settings.STORAGE_DIR, 'artists.pickle'), 'rb') as f:
        artists = pickle.load(f)
    artists = dict([(aid, artists[aid]) for aid in artists.keys()][:100])
    documents = [get_document_by_aid(aid) for aid in artists.keys()]
    tfidf = TfidfVectorizer(
        tokenizer=verb_tokenizer,
        stop_words=stopwords,
        max_df=0.80
    )
    tfs = tfidf.fit_transform(documents)

    result = []
    for aidx, content in enumerate(artists.keys()):
        hs_idxs = [idx for idx, c in sorted(enumerate(tfs.toarray()[aidx]), key=lambda x: x[1], reverse=True)]
        rev_dic = dict([(idx, c) for c, idx in tfidf.vocabulary_.items()])
        result.append(([(rev_dic[idx], tfs.toarray()[aidx][idx]) for idx in hs_idxs], content, artists[content]))
    return result


def list_high_score_words():
    with open(os.path.join(settings.STORAGE_DIR, 'tfidf_results.pickle'), 'rb') as f:
        results = pickle.load(f)
    rrr = []
    for contents, aid, aname in results:
        topcontents = [c for c, p in contents[:10]]
        tc_pattern = '|'.join(topcontents)
        sentences_uniq = list(set(get_sentences_by_aid(aid)))
        for sent in sentences_uniq:
            tokens = get_raw_list(sent)
            words = sorted([
                t[0]
                for t in tokens
                if t[1] == '動詞' and t[2] == '自立' and re.search(tc_pattern, t[8]) is not None
            ])
            if len(words) > 0:
                rrr.append((words, aid, aname, sent))
    return rrr
