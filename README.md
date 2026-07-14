# Project-of-Information-Science-and-Cultural-Heritage
# Ada Lovelace — LODLAM project

My project for the Information Science and Cultural Heritage course
(DHDK, University of Bologna, 2025–26).

The idea: take the Wikipedia article on Ada Lovelace and turn it into
Linked Open Data. I picked 21 entities from the article (people, places,
works, objects), modelled their relations with CIDOC-CRM and FRBRoo,
encoded the text in TEI/XML, and wrote two Python scripts that convert
the TEI into an HTML page and an RDF dataset (358 triples), all linked
to Wikidata, VIAF, GeoNames and LCSH.

**Open `index.html` for the full documentation and all files.**

## Files

- `01_entities.md` — the entities and their authority IDs
- `02_theoretical_model.md` + `.svg` — relations in plain language
- `03_conceptual_model.md` + `.svg`, `03_ontology.ttl` — the formal model
- `04_ada_lovelace.tei.xml` — the TEI encoding
- `05_tei2html.py` → `05_ada_lovelace.html` — text with clickable entities
- `06_tei2rdf.py` → `06_ada_lovelace.ttl` — the RDF dataset
- `graphviz.svg`, `workflow.svg` — graph and workflow images

## How to run

Needs Python 3. For the RDF script: `pip install rdflib`

```
python3 05_tei2html.py
python3 06_tei2rdf.py
```

Both read `04_ada_lovelace.tei.xml` from the same folder.

---

Mayank Nautiyal · source text from Wikipedia (CC BY-SA 4.0) ·
portrait from Wikimedia Commons (public domain)

