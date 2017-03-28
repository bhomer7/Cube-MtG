import urllib.request

from bs4 import BeautifulSoup


def split_and_cut(s, txt, ind, *args):
    """
    Split a string on a sequence of txt arguments and pull out specific indexes.

    Assumes at least one of find, sind is not None
    """
    ret_list = s.split(txt)
    if isinstance(ind, tuple):
        find, sind = ind
        if find is None:
            ret_list = ret_list[:sind]
        elif sind is None:
            ret_list = ret_list[find:]
        else:
            ret_list = ret_list[find:sind]
        ret = txt.join(ret_list)
    else:
        ret = ret_list[ind]
    if len(args) > 0:
        return split_and_cut(ret, *args)
    else:
        return ret


colors = ['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless']


def get_color_identity(card_lines):
    """
    Get a set of colors in the cards color identity. Card passed as two lines from a dec file.
    """
    res = set()

    mvid = split_and_cut(card_lines, 'mvid:', 1, ' ', 0)
    r_url = 'http://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid={}'.format(mvid)
    doc = None
    req = urllib.request.urlopen(r_url)
    doc = BeautifulSoup(req.read(), "lxml")
    req.close()

    search_items = doc.find_all(**{'class': 'manaRow'})
    search_items += doc.find_all(**{'class': 'cardtextbox'})
    for item in search_items:
        image_items = item.find_all('img')
        for img in image_items:
            possibles = img.get('alt')
            if possibles is None:
                continue
            possibles.replace('Variable Colorless', '')
            for color in colors:
                if color in possibles:
                    res.add(color)
    return res
