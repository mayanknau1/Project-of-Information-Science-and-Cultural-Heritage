import sys
import xml.etree.ElementTree as ET
from html import escape

TEI_NS = '{http://www.tei-c.org/ns/1.0}'
XML_NS = '{http://www.w3.org/XML/1998/namespace}'

def tei(tag: str) -> str:
    """Return the fully-qualified TEI tag, e.g. tei('persName')."""
    return TEI_NS + tag

def build_entity_index(root):
    idx = {}
    # people
    for person in root.iter(tei('person')):
        xid = person.get(XML_NS + 'id')
        if not xid:
            continue
        name_el = None
        for n in person.findall(tei('persName')):
            if n.get('type') == 'main':
                name_el = n
                break
        if name_el is None:
            name_el = person.find(tei('persName'))
        label = person_label(name_el)
        url = pick_authority_url(person, preferred=['wikidata', 'viaf', 'lccn'])
        idx[xid] = {'label': label, 'type': 'person', 'url': url}
    # places
    for place in root.iter(tei('place')):
        xid = place.get(XML_NS + 'id')
        if not xid:
            continue
        name_el = place.find(tei('placeName'))
        label = collapse(name_el) if name_el is not None else xid
        url = pick_authority_url(place, preferred=['geonames', 'wikidata'])
        idx[xid] = {'label': label, 'type': 'place', 'url': url}
    # organisations
    for org in root.iter(tei('org')):
        xid = org.get(XML_NS + 'id')
        if not xid:
            continue
        name_el = org.find(tei('orgName'))
        label = collapse(name_el) if name_el is not None else xid
        url = pick_authority_url(org, preferred=['wikidata', 'viaf'])
        idx[xid] = {'label': label, 'type': 'org', 'url': url}
    # objects (machines, programming language)
    for obj in root.iter(tei('object')):
        xid = obj.get(XML_NS + 'id')
        if not xid:
            continue
        name_el = obj.find('.//' + tei('objectName'))
        label = collapse(name_el) if name_el is not None else xid
        url = pick_authority_url(obj, preferred=['wikidata', 'lcsh'])
        idx[xid] = {'label': label, 'type': 'object', 'url': url}
    # bibliographic works
    src = root.find('.//' + tei('sourceDesc'))
    if src is not None:
        for bibl in src.iter(tei('bibl')):
            xid = bibl.get(XML_NS + 'id')
            if not xid:
                continue
            title_el = bibl.find(tei('title'))
            label = collapse(title_el) if title_el is not None else xid
            url = pick_authority_url(bibl, preferred=['wikidata'])
            if not url:
                ref_el = bibl.find(tei('ref'))
                if ref_el is not None:
                    url = ref_el.get('target')
            idx[xid] = {'label': label, 'type': 'work', 'url': url}

    return idx


def pick_authority_url(parent, preferred):
    lookup = {}
    for idno in parent.findall(tei('idno')):
        t = (idno.get('type') or '').lower()
        if t and idno.text:
            lookup[t] = idno.text.strip()
    for t in preferred:
        if t in lookup:
            return lookup[t]
    return None


def collapse(el):
    if el is None:
        return ''
    return ' '.join(''.join(el.itertext()).split())


def person_label(persname_el):
    if persname_el is None:
        return ''
    parts = []
    has_children = False
    for child in persname_el:
        has_children = True
        text = collapse(child)
        if text:
            parts.append(text)
    if has_children:
        return ' '.join(parts)
    return collapse(persname_el)


def render_inline(el, idx):
    tag = el.tag.replace(TEI_NS, '')
    if tag == 'persName':
        return wrap_entity(el, idx, 'person')
    if tag == 'placeName':
        return wrap_entity(el, idx, 'place')
    if tag == 'orgName':
        return wrap_entity(el, idx, 'org')
    if tag == 'objectName':
        return wrap_entity(el, idx, 'object')
    if tag == 'name':
        return wrap_entity(el, idx, 'object')
    if tag == 'bibl':
        return wrap_entity(el, idx, 'bibl')
    if tag == 'title':
        return f'<em class="title">{children_html(el, idx)}</em>'
    if tag == 'term':
        ref = el.get('ref', '')
        label = escape(el.text or '')
        if ref.startswith('http'):
            return f'<a class="entity concept" href="{escape(ref)}">{label}</a>'
        return f'<span class="entity concept">{label}</span>'
    if tag == 'date':
        when = el.get('when') or el.get('from') or ''
        label = escape(el.text or '')
        if when:
            return f'<time datetime="{escape(when)}" class="date">{label}</time>'
        return f'<span class="date">{label}</span>'
    if tag == 'quote':
        return f'<q>{children_html(el, idx)}</q>'
    if tag == 'hi':
        return f'<span class="hi">{children_html(el, idx)}</span>'

    return children_html(el, idx)


def wrap_entity(el, idx, css_class):
    ref = el.get('ref', '') or ''
    inner = children_html(el, idx) if list(el) else escape(el.text or '')

    if ref.startswith('#'):
        entry = idx.get(ref[1:])
        if entry and entry.get('url'):
            tooltip = escape(entry['label'])
            return (f'<a class="entity {css_class}" href="{escape(entry["url"])}" '
                    f'title="{tooltip}">{inner}</a>')
        return f'<span class="entity {css_class}">{inner}</span>'
    if ref.startswith('http'):
        return f'<a class="entity {css_class}" href="{escape(ref)}">{inner}</a>'
    return f'<span class="entity {css_class}">{inner}</span>'


def children_html(el, idx):
    out = []
    if el.text:
        out.append(escape(el.text))
    for child in el:
        out.append(render_inline(child, idx))
        if child.tail:
            out.append(escape(child.tail))
    return ''.join(out)


def render_body(root, idx):
    body = root.find('.//' + tei('body'))
    parts = []
    for top_div in body.findall(tei('div')):
        parts.append('<article>')
        for child in top_div:
            tag = child.tag.replace(TEI_NS, '')
            if tag == 'head':
                # already rendered as page <h1> in the header; skip here
                continue
            if tag == 'div':
                sec_id = child.get(XML_NS + 'id', '')
                parts.append(f'<section id="{escape(sec_id)}">')
                for sub in child:
                    sub_tag = sub.tag.replace(TEI_NS, '')
                    if sub_tag == 'head':
                        parts.append(f'<h2>{children_html(sub, idx)}</h2>')
                    elif sub_tag == 'p':
                        parts.append(f'<p>{children_html(sub, idx)}</p>')
                    else:
                        parts.append(render_inline(sub, idx))
                parts.append('</section>')
            elif tag == 'p':
                parts.append(f'<p>{children_html(child, idx)}</p>')
        parts.append('</article>')
    return '\n'.join(parts)

def build_html(title, body_html, idx, source_url):
    rows = []
    for xid, e in sorted(idx.items()):
        url = e.get('url') or ''
        url_html = (f'<a href="{escape(url)}">{escape(url)}</a>' if url else '—')
        rows.append(
            f'<tr><td><code>#{escape(xid)}</code></td>'
            f'<td>{escape(e["label"])}</td>'
            f'<td>{escape(e["type"])}</td>'
            f'<td>{url_html}</td></tr>'
        )
    index_rows = '\n'.join(rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{escape(title)} — TEI to HTML</title>
<style>
  body {{
    font-family: Georgia, "Times New Roman", serif;
    max-width: 820px;
    margin: 2em auto;
    padding: 0 1em;
    line-height: 1.65;
    color: #222;
    background: #fafaf6;
  }}
  header h1 {{
    font-size: 2.2em;
    margin-bottom: .1em;
    border-bottom: 3px solid #B58900;
    padding-bottom: .2em;
    color: #222;
  }}
  h2 {{ font-size: 1.35em; color: #5D4500; margin-top: 2em; }}

  a {{ text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}

  .entity {{ border-bottom: 1px dotted #888; padding-bottom: 1px; }}
  .entity.person   {{ color: #1565C0; }}
  .entity.place    {{ color: #2E7D32; }}
  .entity.org      {{ color: #6A1B9A; }}
  .entity.object   {{ color: #512DA8; font-weight: 500; }}
  .entity.concept  {{ color: #B85C44; font-style: italic; }}
  .entity.bibl     {{ color: #9E8400; }}

  .title {{ font-style: italic; }}
  .date  {{ color: #555; font-variant-numeric: tabular-nums; }}
  q      {{ font-style: italic; }}
  q::before {{ content: '\\201C'; }}
  q::after  {{ content: '\\201D'; }}

  .meta {{
    background: #FFFEF0;
    border-left: 4px solid #B58900;
    padding: 1em;
    margin: 1.5em 0;
    font-size: 0.92em;
    color: #5D4500;
  }}
  .legend {{ font-size: 0.85em; color: #666; margin: .5em 0 2em; }}
  .legend .swatch {{ display: inline-block; margin-right: 1.4em; }}
  .legend .dot {{
    display: inline-block; width: 10px; height: 10px;
    border-radius: 50%; margin-right: 4px; vertical-align: middle;
  }}

  hr {{ border: none; border-top: 1px solid #d8d2bb; margin: 3em 0; }}

  table.index {{
    width: 100%; border-collapse: collapse;
    font-size: 0.9em; margin-top: 1em;
    background: white;
  }}
  table.index th {{
    background: #FFF8C5; text-align: left;
    padding: .5em .6em; border-bottom: 2px solid #B58900;
    color: #5D4500;
  }}
  table.index td {{
    padding: .4em .6em;
    border-bottom: 1px solid #eee;
    vertical-align: top;
  }}
  table.index code {{
    background: #f0ecdf;
    padding: 1px 5px; border-radius: 3px;
    font-size: 0.95em;
  }}
  footer {{ font-size: .85em; color: #777; margin-top: 3em; }}
</style>
</head>
<body>

<header>
  <h1>{escape(title)}</h1>
  <div class="meta">
    <strong>Source:</strong> English Wikipedia,
    <em>Ada Lovelace</em>
    (<a href="{escape(source_url)}">{escape(source_url)}</a>).<br>
    <strong>Encoding:</strong> TEI All XML transformed to HTML by
    <code>05_tei2html.py</code>.<br>
    <strong>Authority alignment:</strong> VIAF · Wikidata · GeoNames · LCSH / LCCN.
  </div>
  <div class="legend">
    <span class="swatch"><span class="dot" style="background:#1565C0"></span>person</span>
    <span class="swatch"><span class="dot" style="background:#2E7D32"></span>place</span>
    <span class="swatch"><span class="dot" style="background:#6A1B9A"></span>organisation</span>
    <span class="swatch"><span class="dot" style="background:#512DA8"></span>object</span>
    <span class="swatch"><span class="dot" style="background:#B85C44"></span>concept</span>
    <span class="swatch"><span class="dot" style="background:#9E8400"></span>bibliographic work</span>
  </div>
</header>

{body_html}

<hr>
<h2>Entity index</h2>
<p>The {len(idx)} entities annotated in this document, with their local
<code>xml:id</code>, type, and resolved authority URI. Click any in-text
annotation above to open its record on Wikidata / VIAF / GeoNames.</p>
<table class="index">
  <thead>
    <tr><th>Local id</th><th>Label</th><th>Type</th><th>Authority URI</th></tr>
  </thead>
  <tbody>
{index_rows}
  </tbody>
</table>

<hr>
<footer>
  Ada Lovelace LODLAM project · Information Science and Cultural Heritage,
  a.y. 2025–2026.<br>
  Generated from <code>04_ada_lovelace.tei.xml</code> by <code>05_tei2html.py</code>.
</footer>

</body>
</html>
"""

def main(infile, outfile):
    tree = ET.parse(infile)
    root = tree.getroot()

    idx = build_entity_index(root)

    title = collapse(root.find('.//' + tei('titleStmt') + '/' + tei('title')))
    source_url = ''
    for ref in root.iter(tei('ref')):
        t = ref.get('target', '')
        if 'wikipedia.org' in t:
            source_url = t
            break

    body_html = render_body(root, idx)
    html = build_html(title, body_html, idx, source_url)

    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'Wrote {outfile}')
    print(f'  {len(idx)} entities indexed')
    for kind in ('person', 'place', 'org', 'object', 'work'):
        n = sum(1 for e in idx.values() if e['type'] == kind)
        print(f'  {n} {kind}s')


if __name__ == '__main__':
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 1:
        main('04_ada_lovelace.tei.xml', '05_ada_lovelace.html')
    else:
        print('Usage: python3 05_tei2html.py [INPUT.xml OUTPUT.html]', file=sys.stderr)
        sys.exit(1)
