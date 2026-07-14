
import sys
import xml.etree.ElementTree as ET
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, DC, DCTERMS, SKOS, XSD

TEI = '{http://www.tei-c.org/ns/1.0}'
XML = '{http://www.w3.org/XML/1998/namespace}'


def tei(tag):
    return TEI + tag

CRM    = Namespace('http://www.cidoc-crm.org/cidoc-crm/')
FRBROO = Namespace('http://erlangen-crm.org/efrbroo/')

BASE    = 'https://w3id.org/adalovelaceproject/'
PROJ    = Namespace(BASE)
PERSON  = Namespace(BASE + 'person/')
PLACE   = Namespace(BASE + 'place/')
ORG     = Namespace(BASE + 'org/')
WORK    = Namespace(BASE + 'work/')
MANIF   = Namespace(BASE + 'manifestation/')
EVENT   = Namespace(BASE + 'event/')
OBJ     = Namespace(BASE + 'object/')
CONCEPT = Namespace(BASE + 'concept/')
TS      = Namespace(BASE + 'timespan/')
TYPE    = Namespace(BASE + 'type/')


def bind_namespaces(g):
    """Register every prefix with the graph so the Turtle output is
    readable (person:ada instead of the full URI)."""
    for prefix, ns in [('', PROJ), ('person', PERSON), ('place', PLACE),
                       ('org', ORG), ('work', WORK), ('manif', MANIF),
                       ('event', EVENT), ('obj', OBJ), ('concept', CONCEPT),
                       ('ts', TS), ('type', TYPE),
                       ('crm', CRM), ('frbroo', FRBROO),
                       ('dc', DC), ('dcterms', DCTERMS), ('skos', SKOS),
                       ('owl', OWL), ('rdfs', RDFS)]:
        g.bind(prefix, ns)

def collapse(el):
    if el is None:
        return ''
    return ' '.join(''.join(el.itertext()).split())


def person_label(p):
    name = None
    for n in p.findall(tei('persName')):
        if n.get('type') == 'main':
            name = n
            break
    if name is None:
        name = p.find(tei('persName'))
    if name is None:
        return ''
    parts = [collapse(c) for c in name]
    parts = [x for x in parts if x]
    return ' '.join(parts) if parts else collapse(name)


def get_idnos(el):
    out = {}
    for idno in el.findall(tei('idno')):
        t = (idno.get('type') or '').lower()
        if t and idno.text:
            out[t] = idno.text.strip()
    return out


def add_timespan(g, ev_uri, when):
    ts = TS[when]
    g.add((ts, RDF.type, CRM['E52_Time-Span']))
    g.add((ts, RDFS.label, Literal(when)))
    g.add((ts, CRM.P82_at_some_time_within, Literal(when, datatype=XSD.date)))
    g.add((ev_uri, CRM['P4_has_time-span'], ts))

def emit_persons(g, root):
    for p in root.iter(tei('person')):
        xid = p.get(XML + 'id')
        if not xid:
            continue
        uri = PERSON[xid]
        label = person_label(p)

        g.add((uri, RDF.type, CRM.E21_Person))
        if label:
            g.add((uri, RDFS.label, Literal(label, lang='en')))

        for _, url in get_idnos(p).items():
            g.add((uri, OWL.sameAs, URIRef(url)))

        for occ in p.findall(tei('occupation')):
            if occ.text:
                g.add((uri, DC.description, Literal(occ.text.strip(), lang='en')))

        b = p.find(tei('birth'))
        if b is not None:
            ev = EVENT[xid + '_birth']
            g.add((ev, RDF.type, CRM.E67_Birth))
            g.add((ev, CRM.P98_brought_into_life, uri))
            g.add((ev, RDFS.label, Literal(f'Birth of {label}', lang='en')))
            if b.get('when'):
                add_timespan(g, ev, b.get('when'))
            pl = b.find(tei('placeName'))
            if pl is not None and (pl.get('ref') or '').startswith('#'):
                g.add((ev, CRM.P7_took_place_at, PLACE[pl.get('ref')[1:]]))

        d = p.find(tei('death'))
        if d is not None:
            ev = EVENT[xid + '_death']
            g.add((ev, RDF.type, CRM.E69_Death))
            g.add((ev, CRM.P100_was_death_of, uri))
            g.add((ev, RDFS.label, Literal(f'Death of {label}', lang='en')))
            if d.get('when'):
                add_timespan(g, ev, d.get('when'))
            pl = d.find(tei('placeName'))
            if pl is not None and (pl.get('ref') or '').startswith('#'):
                g.add((ev, CRM.P7_took_place_at, PLACE[pl.get('ref')[1:]]))


def emit_places(g, root):
    for p in root.iter(tei('place')):
        xid = p.get(XML + 'id')
        if not xid:
            continue
        uri = PLACE[xid]
        g.add((uri, RDF.type, CRM.E53_Place))
        name = p.find(tei('placeName'))
        if name is not None:
            g.add((uri, RDFS.label, Literal(collapse(name), lang='en')))
        for _, url in get_idnos(p).items():
            g.add((uri, OWL.sameAs, URIRef(url)))


def emit_orgs(g, root):
    for o in root.iter(tei('org')):
        xid = o.get(XML + 'id')
        if not xid:
            continue
        uri = ORG[xid]
        g.add((uri, RDF.type, CRM.E74_Group))
        name = o.find(tei('orgName'))
        if name is not None:
            g.add((uri, RDFS.label, Literal(collapse(name), lang='en')))
        for _, url in get_idnos(o).items():
            g.add((uri, OWL.sameAs, URIRef(url)))


def emit_objects(g, root):
    for o in root.iter(tei('object')):
        xid = o.get(XML + 'id')
        if not xid:
            continue
        uri = OBJ[xid]
        g.add((uri, RDF.type, CRM['E22_Human-Made_Object']))
        name = o.find('.//' + tei('objectName'))
        if name is not None:
            g.add((uri, RDFS.label, Literal(collapse(name), lang='en')))
        for _, url in get_idnos(o).items():
            g.add((uri, OWL.sameAs, URIRef(url)))


def emit_works(g, root):
    src = root.find('.//' + tei('sourceDesc'))
    if src is None:
        return
    for b in src.iter(tei('bibl')):
        xid = b.get(XML + 'id')
        if not xid:
            continue
        uri = WORK[xid]
        g.add((uri, RDF.type, FRBROO.F2_Expression))

        title = b.find(tei('title'))
        if title is not None:
            g.add((uri, DC.title, Literal(collapse(title), lang='en')))
            g.add((uri, RDFS.label, Literal(collapse(title), lang='en')))

        for au in b.findall(tei('author')):
            c = au.get('corresp')
            if c and c.startswith('#'):
                g.add((uri, DCTERMS.creator, PERSON[c[1:]]))

        pub = b.find(tei('publisher'))
        if pub is not None and pub.text:
            g.add((uri, DC.publisher, Literal(pub.text.strip(), lang='en')))
        pp = b.find(tei('pubPlace'))
        if pp is not None and pp.text:
            g.add((uri, DCTERMS.spatial, Literal(pp.text.strip(), lang='en')))
        d = b.find(tei('date'))
        if d is not None and (d.get('when') or d.text):
            g.add((uri, DC.date, Literal(d.get('when') or d.text.strip())))

        for _, url in get_idnos(b).items():
            g.add((uri, OWL.sameAs, URIRef(url)))

def emit_types(g):
    for name in ('Tutoring', 'Collaboration', 'Burial',
                 'Introduction', 'Translation'):
        u = TYPE[name]
        g.add((u, RDF.type, CRM.E55_Type))
        g.add((u, RDFS.label, Literal(name, lang='en')))

def emit_concepts(g):
    scheme = CONCEPT['scheme']
    g.add((scheme, RDF.type, SKOS.ConceptScheme))
    g.add((scheme, DC.title, Literal('Ada Lovelace project subject scheme', lang='en')))
    items = [
        ('computing', 'Computing',
         'http://id.loc.gov/authorities/subjects/sh85029552'),
        ('mathematics', 'Mathematics',
         'http://id.loc.gov/authorities/subjects/sh85082139'),
        ('bernoulli_numbers', 'Bernoulli numbers',
         'http://www.wikidata.org/entity/Q1338141'),
        ('poetical_science', 'Poetical science', None),
    ]
    for slug, label, same in items:
        c = CONCEPT[slug]
        g.add((c, RDF.type, SKOS.Concept))
        g.add((c, SKOS.prefLabel, Literal(label, lang='en')))
        g.add((c, SKOS.inScheme, scheme))
        if same:
            g.add((c, OWL.sameAs, URIRef(same)))


def emit_engine(g, root):
    ae = OBJ['analytical_engine']
    if not root.findall('.//' + tei('object')):        
        g.add((ae, RDF.type, CRM['E22_Human-Made_Object']))
        g.add((ae, RDFS.label, Literal('Analytical Engine', lang='en')))
        g.add((ae, OWL.sameAs, URIRef('http://www.wikidata.org/entity/Q437619')))
        g.add((ae, OWL.sameAs, URIRef('http://id.loc.gov/authorities/subjects/sh85005332')))

    design = EVENT['analytical_engine_design']
    g.add((design, RDF.type, CRM.E12_Production))
    g.add((design, RDFS.label,
           Literal('Design of the Analytical Engine by Charles Babbage', lang='en')))
    g.add((design, CRM.P14_carried_out_by, PERSON['babbage']))
    g.add((design, CRM.P108_has_produced, ae))


def emit_translation_event(g):
    ev = EVENT['translation_1842_1843']
    g.add((ev, RDF.type, FRBROO.F28_Expression_Creation))
    g.add((ev, RDFS.label,
           Literal('Translation of Menabrea and creation of the Notes (1842–43)', lang='en')))
    g.add((ev, CRM.P14_carried_out_by, PERSON['ada']))
    g.add((ev, CRM.P2_has_type, TYPE['Translation']))         
    g.add((ev, CRM.P11_had_participant, PERSON['wheatstone'])) 

    ts = TS['1842_1843']
    g.add((ts, RDF.type, CRM['E52_Time-Span']))
    g.add((ts, RDFS.label, Literal('1842–1843', lang='en')))
    g.add((ts, CRM.P82a_begin_of_the_begin, Literal('1842-01-01', datatype=XSD.date)))
    g.add((ts, CRM.P82b_end_of_the_end,     Literal('1843-12-31', datatype=XSD.date)))
    g.add((ev, CRM['P4_has_time-span'], ts))

    g.add((ev, FRBROO.R17_created, WORK['notes_1843']))
    g.add((ev, FRBROO.R18_created, MANIF['notes_1843_taylor']))

    m = MANIF['notes_1843_taylor']
    g.add((m, RDF.type, FRBROO.F4_Manifestation_Singleton))
    g.add((m, RDFS.label,
           Literal("The Notes in Taylor's Scientific Memoirs, vol. 3 (1843)", lang='en')))
    g.add((m, DC.publisher, Literal('Richard and John E. Taylor', lang='en')))
    g.add((m, DC.date, Literal('1843', datatype=XSD.gYear)))

    w = WORK['notes_work']
    g.add((w, RDF.type, FRBROO.F1_Work))
    g.add((w, RDFS.label, Literal('The Notes (work)', lang='en')))
    g.add((w, FRBROO.R3_is_realised_in, WORK['notes_1843']))

    e = WORK['notes_1843']
    g.add((e, FRBROO.R76_is_derivative_of, WORK['menabrea_1842'])) 
    g.add((e, CRM.P148_has_component, WORK['note_g']))              
    g.add((e, CRM.P129_is_about, OBJ['analytical_engine']))         
    g.add((e, DCTERMS.subject, CONCEPT['computing']))
    g.add((e, DCTERMS.subject, CONCEPT['mathematics']))

    g.add((WORK['note_g'], CRM.P129_is_about, OBJ['analytical_engine']))
    g.add((WORK['note_g'], CRM.P129_is_about, CONCEPT['bernoulli_numbers']))

    mw = EVENT['menabrea_writing_1842']
    g.add((mw, RDF.type, FRBROO.F28_Expression_Creation))
    g.add((mw, RDFS.label,
           Literal('Writing of the 1842 French article by Luigi Menabrea', lang='en')))
    g.add((mw, CRM.P14_carried_out_by, PERSON['menabrea']))
    g.add((mw, FRBROO.R17_created, WORK['menabrea_1842']))


def emit_biographical_events(g):
    ev = EVENT['ada_burial']
    g.add((ev, RDF.type, CRM.E5_Event))
    g.add((ev, CRM.P2_has_type, TYPE['Burial']))
    g.add((ev, CRM.P11_had_participant, PERSON['ada']))
    g.add((ev, CRM.P7_took_place_at, PLACE['hucknall_church']))
    g.add((ev, RDFS.label, Literal('Burial of Ada Lovelace', lang='en')))

    g.add((EVENT['ada_birth'], CRM.P97_from_father, PERSON['byron']))
    g.add((EVENT['ada_birth'], CRM.P96_by_mother,   PERSON['milbanke']))

    intro = EVENT['introduction_1833']
    g.add((intro, RDF.type, CRM.E5_Event))
    g.add((intro, CRM.P2_has_type, TYPE['Introduction']))
    g.add((intro, RDFS.label,
           Literal('Introduction of Ada to Babbage by Mary Somerville', lang='en')))
    for who in ('ada', 'babbage', 'somerville'):
        g.add((intro, CRM.P11_had_participant, PERSON[who]))
    add_timespan(g, intro, '1833-06-05')

    for tutor in ('somerville', 'demorgan'):
        tu = EVENT['tutoring_by_' + tutor]
        g.add((tu, RDF.type, CRM.E7_Activity))
        g.add((tu, CRM.P2_has_type, TYPE['Tutoring']))
        g.add((tu, CRM.P14_carried_out_by, PERSON[tutor]))
        g.add((tu, CRM.P11_had_participant, PERSON['ada']))
        g.add((tu, RDFS.label, Literal(f'Tutoring of Ada by {tutor}', lang='en')))

    co = EVENT['collaboration_ada_babbage']
    g.add((co, RDF.type, CRM.E7_Activity))
    g.add((co, CRM.P2_has_type, TYPE['Collaboration']))
    g.add((co, CRM.P14_carried_out_by, PERSON['ada']))
    g.add((co, CRM.P14_carried_out_by, PERSON['babbage']))
    g.add((co, RDFS.label,
           Literal('Collaboration between Ada Lovelace and Charles Babbage', lang='en')))


def emit_dataset_metadata(g):
    ds = URIRef(BASE + 'dataset')
    g.add((ds, RDF.type, OWL.Ontology))
    g.add((ds, DC.title, Literal('Ada Lovelace LODLAM project — RDF dataset', lang='en')))
    g.add((ds, DC.creator, Literal('Mr. Tuco', lang='en')))
    g.add((ds, DC.date, Literal('2026', datatype=XSD.gYear)))
    g.add((ds, DC.description, Literal(
        'RDF dataset derived from the TEI-encoded Wikipedia article on Ada '
        'Lovelace, following a CIDOC-CRM + FRBRoo + SKOS + DC + OWL model.',
        lang='en')))

def main(infile, outfile):
    root = ET.parse(infile).getroot()
    g = Graph()
    bind_namespaces(g)

    emit_persons(g, root)
    emit_places(g, root)
    emit_orgs(g, root)
    emit_objects(g, root)
    emit_works(g, root)

    emit_types(g)
    emit_concepts(g)
    emit_engine(g, root)
    emit_translation_event(g)
    emit_biographical_events(g)
    emit_dataset_metadata(g)

    g.serialize(destination=outfile, format='turtle')

    print(f'Wrote {outfile}')
    print(f'  {len(g)} triples')
    from collections import Counter
    census = Counter()
    for s, p, o in g.triples((None, RDF.type, None)):
        short = (str(o).replace(str(CRM), 'crm:')
                       .replace(str(FRBROO), 'frbroo:')
                       .replace(str(SKOS), 'skos:')
                       .replace(str(OWL), 'owl:'))
        census[short] += 1
    for cls, n in census.most_common():
        print(f'    {cls:45} {n}')


if __name__ == '__main__':
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        main('04_ada_lovelace.tei.xml', '06_ada_lovelace.ttl')
