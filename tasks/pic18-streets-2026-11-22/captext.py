"""main_text: the text every quote offset in this packet indexes (controller ruling 2026-11-22: quote from main text only; navigation, header, footer excluded).
Derivation, reproducible: decode the capture bytes as UTF-8 (errors replaced); parse with fetch.Page (stdlib html.parser; drops script, style, noscript, nav, header, footer,
aside, svg, form, select, button, iframe, template, head and any element whose class/id matches the menu-like pattern SKIP_CLASS; block elements start a new line); if that yields
under 200 characters, re-parse with classskip=False (flagged); join the lines with ONE space; collapse whitespace. offset/length index this string (Python str indexes, code points).
Replaces the earlier use of the binding gate's whole-page capture_text, which the controller ruled out."""
import re
import fetch


def main_text(data):
    body = data.decode('utf-8', errors='replace')
    pg = fetch.Page(); pg.feed(body); lines, _ = pg.result()
    if sum(len(t) for t, _ in lines) < 200:
        pg = fetch.Page(classskip=False); pg.feed(body); lines, _ = pg.result()
    return re.sub(r'\s+', ' ', ' '.join(t for t, _ in lines)).strip()


def page_text(data):
    """Visible text of the whole page (script/style/noscript/template skipped, whitespace collapsed): used ONLY to tell 'address present but outside main text' from
    'no address on the page'; never for a quote."""
    from html.parser import HTMLParser
    class T(HTMLParser):
        def __init__(s): super().__init__(convert_charrefs=True); s.p, s.k = [], 0
        def handle_starttag(s, tag, a): s.k += tag in ('script', 'style', 'noscript', 'template')
        def handle_endtag(s, tag): s.k -= tag in ('script', 'style', 'noscript', 'template') and s.k > 0
        def handle_data(s, d):
            if not s.k: s.p.append(d)
    t = T(); t.feed(data.decode('utf-8', errors='replace')); t.close()
    return re.sub(r'\s+', ' ', ' '.join(t.p)).strip()
