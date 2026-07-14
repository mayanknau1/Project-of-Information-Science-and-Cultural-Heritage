# Phase 2 — Theoretical model

This is the natural-language version of the relations between Ada Lovelace and the 20 selected entities. It is the bridge between the entity list (Phase 1) and the formal ontology (Phase 3).

The visual mind map is in `02_theoretical_model.svg`.

## Relations (subject — predicate — object)

### Biographical relations (Ada → people)

- Ada Lovelace **is daughter of** Lord Byron
- Ada Lovelace **is daughter of** e
- Ada Lovelace **married** William King-Noel, 1st Earl of Lovelace *(8 July 1835; she became Countess of Lovelace in 1838)*
- Ada Lovelace **was tutored by** Mary Somerville
- Ada Lovelace **was tutored by** Augustus De Morgan *(Advanced MAth Tutor)*
- Ada Lovelace **collaborated with** Charles Babbage
- Mary Somerville **introduced Ada to** Charles Babbage *(on 5 June 1833, at one of Babbage's Saturday-night soirées)*
- Ada Lovelace **was acquainted with** Michael Faraday
- Ada Lovelace **was acquainted with** Charles Dickens *(Dickens visited her in August 1852 and read to her from* Dombey and Son*)*

### Geographical relations (Ada → places)

- Ada Lovelace **was born in** London *(10 December 1815)*
- Ada Lovelace **died in** London *(27 November 1852)*
- Ada Lovelace **was buried at** the Church of St Mary Magdalene, Hucknall *(next to her father Byron)*
- Charles Babbage **gave a seminar at** the University of Turin, **located in** Turin *(1840, on the Analytical Engine)*

### Creative / bibliographic relations (Ada → works)

- Charles Wheatstone **commissioned** the translation
- Ada Lovelace **carried out** the Translation & publication event of 1842–43
- The Translation & publication event of 1842–43 **produced** the *Sketch of the Analytical Engine… with notes by the translator* (her *Notes*), published in *Taylor's Scientific Memoirs* vol. 3, September 1843
- The 1843 *Sketch / Notes* **translates** Luigi Menabrea's original French article (1842, *Bibliothèque universelle de Genève*)
- The 1843 *Sketch / Notes* **contains** Note G (the Bernoulli-numbers algorithm — "the first published computer program")
- The 1843 *Sketch / Notes* **describes** the Analytical Engine

### Conceptual relations (others → objects and concepts)

- Charles Babbage **designed** the Difference Engine *(Ada saw the working prototype in June 1833)*
- Charles Babbage **designed** the Analytical Engine
- The Analytical Engine **is the successor of** the Difference Engine
- Luigi Menabrea **authored** the 1842 French article about the Analytical Engine
- Augustus De Morgan **taught Ada** the calculus and Bernoulli-numbers theory used in Note G
- The programming language **Ada is named after** Ada Lovelace *(created for the US Department of Defense, 1980)*

## Indirect / inferred relations (worth noting in the model)

- Note G **is the published-program contribution attributed to** Ada Lovelace
- The 1843 *Sketch / Notes* and Menabrea's 1842 article **share the same conceptual subject** (the Analytical Engine) — modelled in CIDOC as `crm:P129_is_about`
- Babbage's Turin seminar **is the indirect origin of** Menabrea's article (Menabrea transcribed the lecture)

## How this maps to the ontology (preview of Phase 3)

| Theoretical concept | Will become in Phase 3 |
|---|---|
| Person (Ada, Babbage, Byron, Milbanke, King-Noel, Somerville, Menabrea, De Morgan, Wheatstone, Faraday, Dickens) | `crm:E21_Person` (subclass of `crm:E39_Actor`) |
| Place (London, Hucknall church, Turin) | `crm:E53_Place` |
| Organisation (University of Turin) | `crm:E74_Group` |
| Work (Ada's *Notes*, Menabrea's article, Note G) | `frbroo:F1_Work` / `frbroo:F2_Expression` / `frbroo:F4_Manifestation_Singleton` |
| Designed object (Analytical Engine, Difference Engine) | `crm:E22_Human-Made_Object` |
| Legacy concept (Ada programming language) | `crm:E28_Conceptual_Object` |
| Event (Translation 1842–43, birth, death, burial, marriage, seminar) | `crm:E5_Event` / `crm:E12_Production` / `frbroo:F28_Expression_Creation` |
| Date / period (1815, 1833, 1835, 1840, 1843, 1852) | `crm:E52_Time-Span` |
| Subject (computing, mathematics, "poetical science") | `skos:Concept` |
| Title / basic metadata | `dc:title`, `dcterms:creator`, `dc:date` |
| Link to external authority (VIAF, Wikidata, GeoNames, LCSH) | `owl:sameAs` |

## Source

All relations are derived from the English Wikipedia article on Ada Lovelace.
