# UMLS Overview
Here's a comprehensive breakdown of the UMLS Metathesaurus project, its VA connection, and how to use it:

---

## What Is the UMLS Metathesaurus?

The **Unified Medical Language System (UMLS)** is a large-scale biomedical knowledge project developed and maintained by the **National Library of Medicine (NLM)**. It is a large biomedical thesaurus organized by concept, or meaning — linking synonymous names from over 200 different source vocabularies. It also identifies useful relationships between concepts and preserves the meanings, concept names, and relationships from each vocabulary.

The UMLS integrates and distributes key terminology, classification and coding standards, and associated resources to promote the creation of more effective and interoperable biomedical information systems and services, including electronic health records.

---

## The VA's Specific Use of UMLS

The **Department of Veterans Affairs (VA)** was one of the most significant institutional users and contributors to UMLS-based research. Their work focused on two major efforts:

**1. VA Medication Reference Terminology**
Researchers at the VA developed and evaluated a UMLS Metathesaurus Co-occurrence mining algorithm to connect medications and the diseases they may treat. Based on 16 years of co-occurrence data, they created 977 candidate drug-disease pairs for a sample of 100 ingredients. The evaluation showed that more than 80% of those candidate drug-disease pairs were rated "APPROPRIATE" by physician raters. The drug-disease pairs were then used to initialize term definitions in an ongoing effort to build a medication reference terminology for the Veterans Health Administration.

**2. Large Scale Vocabulary Test (LSVT)**
The Large Scale Vocabulary Test was designed to evaluate how well the Metathesaurus, plus planned additions, covered the documentation needs of clinicians. The VA/University of Utah consortium collected over 10,000 clinical narratives from patient problem lists to validate whether existing vocabulary standards could cover real-world clinical language used by VA providers.

**3. Semantic Normal Form for Clinical Drugs**
Using the VA's National Drug File as a starting point, researchers worked to develop a Semantic Normal Form (SNF) to represent orderable drugs, testing whether medications from real-world VA information systems could be modeled in a structured way, and whether clinical drug concepts from disparate vocabularies with considerable naming variation could be declared synonymous.

---

## The Three Core Sections of UMLS

### 1. 🗂️ The Metathesaurus
The Metathesaurus forms the base of the UMLS and comprises over 1 million biomedical concepts and 5 million concept names, all of which stem from over 100 incorporated controlled vocabularies and classification systems. These include SNOMED CT, RxNorm, LOINC, MeSH, CPT, ICD-10-CM, MedDRA, Human Phenotype Ontology, and more.

The Metathesaurus reflects and preserves the meanings, concept names, and relationships from its source vocabularies. When two different source vocabularies use the same name for differing concepts, the Metathesaurus represents both meanings and indicates which meaning is present in which source vocabulary.

### 2. 🔗 The Semantic Network
The UMLS Semantic Network consists of a set of broad subject categories (Semantic Types) that provide consistent categorization of all concepts represented in the Metathesaurus, and a set of useful relationships (Semantic Relations) that exist between those Semantic Types. There are 127 semantic types and 54 relationships in total. The major semantic types are organisms, anatomical structures, biologic function, chemicals, events, physical objects, and concepts or ideas.

### 3. 📖 The SPECIALIST Lexicon & Lexical Tools
The SPECIALIST Lexicon contains information about common English vocabulary, biomedical terms, terms found in MEDLINE, and terms found in the UMLS Metathesaurus. Each entry contains syntactic (how words are put together), morphological (form and structure), and orthographic (spelling) information. A set of Java programs uses the lexicon to work through variations in biomedical texts by relating words by their parts of speech, which can be helpful in web searches or searches through an electronic medical record.

---

## How to Access and Use UMLS

### Step 1: Get a License
UMLS licenses are issued only to individuals, not to groups or organizations. You must accept the terms of the UMLS Metathesaurus License and create a UMLS Terminology Services (UTS) account for access to the UMLS, terminology browsers, and related resources such as RxNorm and SNOMED CT. There is no charge for licensing any part of the UMLS from NLM.

### Step 2: Choose Your Access Method
The UMLS Terminology Services (UTS) provides three ways to access the UMLS: the **Metathesaurus Browser** (retrieve UMLS concept information, including CUIs, semantic types, and synonymous terms), the **Semantic Network Browser** (view the names, definitions, and hierarchical structure of the Semantic Network), and the **UMLS API** (programmatically search and retrieve UMLS data).

### Step 3: Use the Browser or API

**Browser Use:** The UTS allows the user to request information about particular Metathesaurus concepts, including attributes such as the concept's definition, its semantic types, and related concepts. Basic concept information includes the Metathesaurus unique identifier (CUI), the preferred name for the concept, and the names and sources of all terms that comprise that concept.

**API Use:** You can search for partial matches using the search endpoint with `partialSearch=true`, search for a CUI and return a source-asserted code (e.g., a SNOMED CT code), and download any RxNorm, SNOMED CT, or UMLS release programmatically using a single command with your API key.

**Local Installation:** To install the UMLS on your computer, you download the files. The **MetamorphoSys** tool, included with the downloaded files, allows you to customize the UMLS according to your needs. You can then load your customized data into your own database system, such as MySQL or Oracle.

---

## Key Practical Applications

The UMLS is used to power things like:

- **EHR Interoperability** — mapping terms between hospital systems that use different vocabularies (e.g., one using ICD-10, another using SNOMED CT)
- **Clinical NLP** — tools like **MetaMap** take free-text clinical notes and automatically identify UMLS concepts within them
- **Drug Safety Research** — as the VA demonstrated, mining co-occurrences to find drug-disease relationships at scale
- **Decision Support Systems** — building terminology-aware alerts and recommendations inside clinical software
- Enhancing or developing applications such as electronic health records, classification tools, dictionaries, and language translators

In short, UMLS is the "Rosetta Stone" of biomedical vocabulary — and the VA was a pioneering institution in proving how it could be used to standardize and improve real-world clinical care at massive scale.
