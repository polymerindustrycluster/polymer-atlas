"""Classify where a quote sits in the stored page: navigation chrome vs content, and article-like URL paths.

nav_only(html, quote): True when every occurrence of the quote's words (in order) lies inside nav/header/footer/menu markup.
article_url(url): True for blog, news, article or guide paths (a process explainer is not the company's own market statement).
shortcut: stdlib HTMLParser, void-tag/unclosed-tag handling is approximate; a True result is a review prompt, not proof.
"""
import re
from html.parser import HTMLParser
from urllib.parse import urlparse

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
CHROME_TAG = {'nav', 'header', 'footer', 'aside'}
CHROME_TOKEN = re.compile(r'(site-|main-|page-|mobile-)?(nav|navbar|navigation|menu|footer|header|breadcrumbs?|dropdown|megamenu)(-[a-z0-9]+)*|.*[-_](menu|nav|navbar)([-_].*)?', re.I)
NEGATED = re.compile(r'(^|[-_])(not|no|but|has)[-_]|style-menu', re.I)  # wsite-not-footer, all-but-footer, page-has-no-sidebar, quick-text-style-menu


def chrome_attr(value):
    return any(CHROME_TOKEN.fullmatch(t) and not NEGATED.search(t) for t in (value or '').split())


ARTICLE_PATH = re.compile(r'/(blog|news|article|articles|post|posts|insights|resources|learn|guide|guides|what-|how-|why-)', re.I)


def norm_words(s):
    return re.findall(r'\w+', s.lower())


class _Nodes(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.nodes, self.skip = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        a = dict(attrs)
        wrapper = tag in ('html', 'body', 'main')  # page builders put menu classes on the body; not chrome
        chrome = tag in CHROME_TAG or (not wrapper and chrome_attr(' '.join(filter(None, [a.get('class'), a.get('id'), a.get('role')]))))
        self.stack.append((tag, chrome))
        self.skip += tag in ('script', 'style', 'noscript')

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for t, _ in self.stack[i:]:
                    self.skip -= t in ('script', 'style', 'noscript')
                del self.stack[i:]
                return

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.nodes.append((data, any(c for _, c in self.stack)))


def occurrences(html, quote):
    """Yield, per occurrence of the quote's words in order, whether every covering text node sits in page chrome."""
    p = _Nodes()
    p.feed(html)
    words, flags = [], []
    for data, chrome in p.nodes:
        for w in norm_words(data):
            words.append(w)
            flags.append(chrome)
    q = norm_words(quote)
    n = len(q)
    return [all(flags[i:i + n]) for i in range(len(words) - n + 1) if words[i:i + n] == q] if n else []


def nav_only(html, quote):
    occ = occurrences(html, quote)
    return bool(occ) and all(occ)


def article_url(url):
    return bool(ARTICLE_PATH.search(urlparse(url).path))
