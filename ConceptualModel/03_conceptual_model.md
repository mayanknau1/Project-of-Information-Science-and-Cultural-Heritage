# Phase 3 — Conceptual model (formal ontology)

This phase refines the Phase 2 theoretical model into formal terms taken from existing, well-established ontologies. Following the requirement in the project guidelines, we **reuse existing vocabularies** rather than minting new terms wherever possible, and document the rationale for every choice.

## 1. Namespaces used

| Prefix | URI | Used for |
|---|---|---|
| `crm:` | `http://www.cidoc-crm.org/cidoc-crm/` | CIDOC Conceptual Reference Model — backbone of the ontology (events, actors, places, time-spans, physical objects). ISO 21127 standard for cultural heritage. |
| `frbroo:` | `http://erlangen-crm.org/efrbroo/` | FRBR object-oriented — used for the bibliographic levels (Work, Expression, Manifestation) of Ada's *Notes*, Note G, and Menabrea's article. Fully aligned with CIDOC-CRM. |
| `skos:` | `http://www.w3.org/2004/02/skos/core#` | Subject classification ("computing", "mathematics", "poetical science"). |
| `dc:` | `http://purl.org/dc/elements/1.1/` | Basic descriptive metadata with literal values (title, date, description). |
| `dcterms:` | `http://purl.org/dc/terms/` | Extended Dublin Core: `dcterms:creator` when the value is a URI, `dcterms:subject` for SKOS links. |
| `foaf:` | `http://xmlns.com/foaf/0.1/` | Lightweight alternative typing and labels: `foaf:Person`, `foaf:name`. |
| `owl:` | `http://www.w3.org/2002/07/owl#` | Authority-file alignment via `owl:sameAs`. |
| `rdf:`, `rdfs:`, `xsd:` | (standard) | RDF infrastructure and datatypes. |
| `:` | `https://w3id.org/adalovelaceproject/` | Our own project namespace for the instances we mint (people, events, works). |

## 2. Class mapping (entity type → ontology class)

For each entity type in Phase 1, we select one primary class. Where two ontologies could fit (e.g. CIDOC `E21_Person` vs FOAF `foaf:Person`), the rationale is given.

| Phase 2 entity type | Phase 3 class | Rationale |
|---|---|---|
| **Person** (Ada, Babbage, Byron, Milbanke, King-Noel, Somerville, Menabrea, De Morgan, Wheatstone, Faraday, Dickens) | `crm:E21_Person` (subclass of `crm:E39_Actor`) | The ontology backbone is CIDOC-CRM and the Venus reference project uses `E21`/`E39`. We also assert `rdf:type foaf:Person` for interoperability. |
| **Place** (London, Hucknall church, Turin) | `crm:E53_Place` | Standard CIDOC class; aligned to GeoNames URIs via `owl:sameAs`. |
| **Organisation** (University of Turin) | `crm:E74_Group` | CIDOC class for collective actors; a university can carry out and host activities. |
| **Designed object** (Analytical Engine; Difference Engine) | `crm:E22_Human-Made_Object` | Human-designed objects. Even though the Analytical Engine was never physically constructed, CIDOC explicitly allows `E22` for designed objects. |
| **Legacy concept** (Ada programming language) | `crm:E28_Conceptual_Object` | A programming language is an immaterial, human-created conceptual product. |
| **Bibliographic work — intellectual content** (the *Notes* as ideas) | `frbroo:F1_Work` | The abstract intellectual content as distinct from its textual realisation; linked to the Expression via `frbroo:R3_is_realised_in`. |
| **Bibliographic work — textual realisation** (the text of the *Notes*, of Note G, of Menabrea's article) | `frbroo:F2_Expression` | The actual textual content. Translations and "contains" relations operate at this level. |
| **Bibliographic work — physical printing** (the 1843 first edition in Taylor's *Scientific Memoirs* vol. 3) | `frbroo:F4_Manifestation_Singleton` | A unique physical instantiation. Same choice as the Venus example. |
| **Translation event (1842–43)** | `frbroo:F28_Expression_Creation` | The FRBRoo class for the creative act that produces an Expression and a Manifestation; typed "Translation" via `crm:P2_has_type`. |
| **Birth / death events** | `crm:E67_Birth` / `crm:E69_Death` | Specialised CIDOC classes, with built-in properties for parents (`P96`, `P97`) and place (`P7`). |
| **Marriage, burial, introduction, visit, acquaintance events** | `crm:E5_Event` typed via `crm:P2_has_type` | CIDOC has no dedicated classes for these; the generic `E5_Event` with an `E55_Type` discriminator is the standard pattern. |
| **Tutoring / collaboration / seminar activities** | `crm:E7_Activity` typed via `crm:P2_has_type` | Generic CIDOC class for intentional activities carried out by actors. |
| **Time-span** (1815, 1833, 1835, 1840, 1842–43, 1852) | `crm:E52_Time-Span` | Standard CIDOC class; literal values via `crm:P82_at_some_time_within` with `xsd:date`. |
| **Subject / topic** (computing, mathematics, "poetical science") | `skos:Concept` | KOS standard for thesaurus concepts; aligned to LCSH where possible. |
| **External authority record** (Wikidata, VIAF, GeoNames, LCSH URIs) | (no class — linked via `owl:sameAs`) | We do not classify the external resource, only declare identity. |

## 3. Property mapping (Phase 2 relation → ontology property)

| Phase 2 relation | Phase 3 property | Pattern |
|---|---|---|
| Ada **is daughter of** Lord Byron | `crm:P97_from_father` *on the birth event* | `:adaBirth crm:P97_from_father :lordByron` |
| Ada **is daughter of** Anne Isabella Milbanke | `crm:P96_by_mother` *on the birth event* | `:adaBirth crm:P96_by_mother :anneIsabellaMilbanke` |
| Ada **was born in** London | `crm:E67_Birth` event with `crm:P7_took_place_at` | `:adaBirth crm:P98_brought_into_life :ada ; crm:P7_took_place_at :london ; crm:P4_has_time-span :ts_1815-12-10` |
| Ada **died in** London | `crm:E69_Death` event with `crm:P7_took_place_at` | `:adaDeath crm:P100_was_death_of :ada ; crm:P7_took_place_at :london ; crm:P4_has_time-span :ts_1852-11-27` |
| Ada **was buried at** St Mary Magdalene | `crm:E5_Event` typed "Burial" | `:adaBurial crm:P11_had_participant :ada ; crm:P7_took_place_at :hucknallChurch` |
| Ada **married** William King-Noel (1835) | `crm:E5_Event` typed "Marriage" with both as participants | `:marriage1835 crm:P11_had_participant :ada, :williamKingNoel ; crm:P4_has_time-span :ts_1835-07-08` |
| Ada **was tutored by** Somerville / De Morgan | `crm:E7_Activity` typed "Tutoring" | `:tutoringBySomerville crm:P14_carried_out_by :marySomerville ; crm:P11_had_participant :ada` |
| Ada **collaborated with** Babbage | `crm:E7_Activity` typed "Collaboration" | `:adaBabbageCollab crm:P14_carried_out_by :ada, :charlesBabbage` |
| Somerville **introduced Ada to** Babbage (5 June 1833) | `crm:E5_Event` typed "Introduction" | `:introduction1833 crm:P11_had_participant :ada, :marySomerville, :charlesBabbage` |
| Ada **was acquainted with** Faraday and Dickens | `crm:E7_Activity` typed "Acquaintance" with all as participants | `:adaAcquaintances crm:P11_had_participant :ada, :michaelFaraday, :charlesDickens` |
| Dickens **visited** Ada (August 1852) | `crm:E5_Event` typed "Visit" | `:dickensVisit1852 crm:P11_had_participant :ada, :charlesDickens ; crm:P4_has_time-span :ts_1852-08` |
| Wheatstone **commissioned** the translation | `crm:P11_had_participant` on the F28 event | `:translationEvent crm:P11_had_participant :charlesWheatstone` |
| Ada **carried out** the Translation event 1842–43 | `crm:P14_carried_out_by` on the F28 event | `:translationEvent crm:P14_carried_out_by :ada` |
| Translation event **produced** the 1843 *Sketch / Notes* | `frbroo:R17_created` (Expression) + `frbroo:R18_created` (Manifestation) | `:translationEvent frbroo:R17_created :notesExpression ; frbroo:R18_created :notesManifestation1843` |
| The Notes as abstract Work **is realised in** the Expression | `frbroo:R3_is_realised_in` (F1 → F2) | `:notesWork frbroo:R3_is_realised_in :notesExpression` |
| The 1843 *Sketch / Notes* **translates** Menabrea's article | `frbroo:R76_is_derivative_of` (F2 → F2) | `:notesExpression frbroo:R76_is_derivative_of :menabreaArticleExpression` |
| The 1843 *Sketch / Notes* **contains** Note G | `crm:P148_has_component` | `:notesExpression crm:P148_has_component :noteG` |
| The 1843 *Sketch / Notes* **is about** the Analytical Engine | `crm:P129_is_about` | `:notesExpression crm:P129_is_about :analyticalEngine` |
| Babbage **designed** the Difference / Analytical Engine | `crm:E12_Production` with `crm:P14_carried_out_by` + `crm:P108_has_produced` | `:analyticalEngineDesign crm:P14_carried_out_by :charlesBabbage ; crm:P108_has_produced :analyticalEngine` |
| Analytical Engine design **continued** the Difference Engine design | `crm:P134_continued` (E7 → E7, between the two design activities) | `:analyticalEngineDesign crm:P134_continued :differenceEngineDesign` |
| Menabrea **authored** the 1842 French article | `frbroo:F28_Expression_Creation` carried out by Menabrea | `:menabreaWriting1842 crm:P14_carried_out_by :luigiMenabrea ; frbroo:R17_created :menabreaArticleExpression` |
| Babbage **gave a seminar at** the University of Turin (1840) | `crm:E7_Activity` typed "Seminar" with the university as participant and Turin as place | `:turinSeminar1840 crm:P14_carried_out_by :charlesBabbage ; crm:P11_had_participant :universityOfTurin ; crm:P7_took_place_at :turin` |
| University of Turin **is located in** Turin | `crm:P74_has_current_or_former_residence` | `:universityOfTurin crm:P74_has_current_or_former_residence :turin` |
| Ada language **is named after** Ada Lovelace | `crm:P67_refers_to` (commemorative reference from the conceptual object to the person) | `:adaLanguage crm:P67_refers_to :ada` |
| Any entity **aligns with** an external authority record | `owl:sameAs` | `:ada owl:sameAs <http://www.wikidata.org/entity/Q7259>, <http://viaf.org/viaf/61632881>` |
| The Notes **is about subject** "computing" / "mathematics" | `dcterms:subject` → `skos:Concept` | `:notesExpression dcterms:subject :concept_computing` |
| Author of a bibliographic item (URI value) | `dcterms:creator` | `:notesExpression dcterms:creator :ada` |
| Basic descriptive metadata (literal values) | `dc:title`, `dc:date`, `dc:description` | Used as lightweight literals alongside the CIDOC structure |

## 4. Worked example (instance graph for the *Notes*)

```
:translationEvent1842-43  rdf:type                frbroo:F28_Expression_Creation ;
                          crm:P2_has_type         :type_Translation ;
                          crm:P14_carried_out_by  :ada ;
                          crm:P11_had_participant :charlesWheatstone ;
                          crm:P4_has_time-span    :ts_1842-1843 ;
                          frbroo:R17_created      :notesExpression ;
                          frbroo:R18_created      :notesManifestation1843 .

:notesWork                rdf:type                frbroo:F1_Work ;
                          frbroo:R3_is_realised_in :notesExpression .

:notesExpression          rdf:type                frbroo:F2_Expression ;
                          dc:title                "Sketch of the Analytical Engine, with notes by the translator"@en ;
                          dcterms:creator         :ada ;
                          crm:P148_has_component  :noteG ;
                          crm:P129_is_about       :analyticalEngine ;
                          frbroo:R76_is_derivative_of :menabreaArticleExpression ;
                          dcterms:subject         :concept_computing .

:notesManifestation1843   rdf:type                frbroo:F4_Manifestation_Singleton ;
                          dc:date                 "1843"^^xsd:gYear .

:noteG                    rdf:type                frbroo:F2_Expression ;
                          dc:title                "Note G"@en ;
                          crm:P129_is_about       :bernoulliNumbersConcept, :analyticalEngine .

:analyticalEngine         rdf:type                crm:E22_Human-Made_Object ;
                          owl:sameAs              <https://www.wikidata.org/wiki/Q485257> .
```

## 5. Why this design? (justification of reuse)

- **CIDOC-CRM** is the ISO standard for cultural-heritage knowledge representation and is event-centric — perfect for biographical data, which is naturally about events (birth, death, marriage, tutoring, collaboration, creation). Every "static" relation of the theoretical model is refactored as an event or activity with participants, following CIDOC best practice.
- **FRBRoo** is fully aligned with CIDOC-CRM and provides the bibliographic granularity (Work / Expression / Manifestation) needed for Ada's *Notes*: the translation relation operates cleanly at the Expression level (`R76`), while the abstract Work level (`F1` + `R3`) records that the Notes exist independently of any single text.
- **SKOS** is the standard for thesaurus-style subject classification and integrates with LCSH.
- **Dublin Core** provides lightweight, universally understood metadata. We follow the DCMI recommendation: `dc:` elements for literal values, `dcterms:` when the value is a resource (e.g. `dcterms:creator` pointing to a person URI).
- **FOAF** adds a widely-consumed typing (`foaf:Person`, `foaf:name`) at near-zero cost.
- **OWL** `sameAs` is the universal mechanism for declaring identity across datasets — required for our alignment to Wikidata, VIAF, GeoNames, LCSH.

Together these vocabularies cover **100%** of the relations identified in Phase 2 without inventing a single new class or property; the only "new" terms are `E55_Type` *instances* (Tutoring, Marriage, Seminar…), which is exactly the extension mechanism CIDOC provides.

## 6. The Graffoo diagram

See `03_conceptual_model.svg` for the visual schema. Conventions follow Graffoo:

- **Yellow rounded rectangles** = classes
- **Solid arrows with labels** = object properties (with the property URI on the arrow)
- **Dashed arrows** = `rdfs:subClassOf`
- **Grey rectangles** = external authority resources (Wikidata, VIAF, GeoNames, LCSH)
