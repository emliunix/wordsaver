# -*- coding: utf-8 -*-

import requests
import lxml.html as lhtml
import lxml.cssselect as cssselect
import re
import itertools

def queryurl(word):
    return "http://cn.bing.com/dict/search?q=%s" % (word, )

def search(word):
    res = requests.get(queryurl(word))
    doc = lhtml.fromstring(res.text)
    w = {}

    # word
    el_word = cssselect.CSSSelector("#headword > h1 > strong")(doc)
    if len(el_word) != 1:
        return None
    w["word"] = el_word[0].text_content()
    
    # pronounces
    el_prons = cssselect.CSSSelector("body > div.contentPadding > div > div > div.lf_area > div.qdef > div.hd_area > div.hd_tf_lh > div > div:nth-child(even) > a")(doc)
    pronounces = {}
    if len(el_prons) > 0:
        if len(el_prons) == 2:
            prEng = el_prons[1].get("onmouseover")
            prEng = re.search(r"https?://.*\.mp3", prEng).group()
            pronounces["eng"] = prEng
        prUs = el_prons[0].get("onmouseover")
        prUs = re.search(r"https?://.*\.mp3", prUs).group()
        pronounces["us"] = prUs
    w["pronounces"] = pronounces

    # definitions
    el_defs = cssselect.CSSSelector("body > div.contentPadding > div > div > div.lf_area > div.qdef > ul > li")(doc)
    definitions = []
    for el in el_defs:
        pos = cssselect.CSSSelector(".pos")(el)[0].text_content()
        defi = cssselect.CSSSelector(".def")(el)[0].text_content()
        definitions.append({"pos": pos, "def": defi})
    w["definitions"] = definitions

    # variants
    el_varis_kind = cssselect.CSSSelector("body > div.contentPadding > div > div > div.lf_area > div.qdef > div.hd_div1 > div > span")(doc)
    el_varis_word = cssselect.CSSSelector("body > div.contentPadding > div > div > div.lf_area > div.qdef > div.hd_div1 > div > a")(doc)
    variants = []
    for (kind, word) in itertools.izip(el_varis_kind, el_varis_word):
        variants.append({
            "kind": kind.text_content(),
            "word": word.text_content()
        })
    w["variants"] = variants

    return w
