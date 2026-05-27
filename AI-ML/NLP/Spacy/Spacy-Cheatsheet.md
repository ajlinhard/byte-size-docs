# spaCy NLP Cheatsheet

> spaCy v3.x · Python 3.8+
> Install: `pip install spacy` · Download model: `python -m spacy download en_core_web_sm`

---

## Setup

```python
import spacy

nlp = spacy.load("en_core_web_sm")   # small model (fast)
# nlp = spacy.load("en_core_web_md") # medium model (word vectors)
# nlp = spacy.load("en_core_web_lg") # large model (best accuracy)

doc = nlp("Apple is looking at buying U.K. startup for $1 billion.")
```

---

## 1. Lexical Analysis

> Tokenization, POS tagging, lemmatization, morphology, stop words

### Tokenization
```python
for token in doc:
    print(token.text)        # raw token text
    print(token.i)           # index in doc
    print(token.is_alpha)    # True if alphabetic
    print(token.is_punct)    # True if punctuation
    print(token.is_space)    # True if whitespace
    print(token.is_stop)     # True if stop word
```

### POS Tagging
```python
for token in doc:
    print(token.text, token.pos_, token.tag_)
    # pos_  → coarse-grained: NOUN, VERB, ADJ, ADV, PROPN, DET...
    # tag_  → fine-grained:   NN, VBZ, JJ, NNP, PRP...

# Explain a tag
spacy.explain("VBZ")   # → "verb, 3rd person singular present"
```

### Lemmatization
```python
for token in doc:
    print(token.text, "→", token.lemma_)
    # "running" → "run", "better" → "good"
```

### Morphology
```python
for token in doc:
    print(token.text, token.morph)
    # Token.morph → MorphAnalysis e.g. Number=Sing|Person=Three|Tense=Pres
    print(token.morph.get("Number"))   # ['Sing']
    print(token.morph.get("Tense"))    # ['Pres']
```

### Filtering Tokens
```python
# Remove stop words and punctuation
clean = [t for t in doc if not t.is_stop and not t.is_punct]

# Keep only nouns and verbs
content = [t for t in doc if t.pos_ in ("NOUN", "VERB", "PROPN")]
```

---

## 2. Semantic Analysis

> Named Entity Recognition (NER), word vectors, similarity, noun chunks

### Named Entity Recognition (NER)
```python
for ent in doc.ents:
    print(ent.text, ent.label_, ent.start_char, ent.end_char)
    # ent.label_  → PERSON, ORG, GPE, DATE, MONEY, PRODUCT...

spacy.explain("GPE")  # → "Countries, cities, states"
```

#### Common NER Labels
| Label    | Meaning                         |
|----------|---------------------------------|
| PERSON   | People, fictional characters    |
| ORG      | Companies, institutions         |
| GPE      | Countries, cities, states       |
| DATE     | Dates, periods                  |
| MONEY    | Monetary values                 |
| PRODUCT  | Products, objects               |
| EVENT    | Named events                    |
| LOC      | Non-GPE locations               |

### Noun Chunks
```python
for chunk in doc.noun_chunks:
    print(chunk.text, chunk.root.text, chunk.root.dep_)
    # e.g. "a U.K. startup" → root: "startup", dep: "dobj"
```

### Word Vectors & Similarity
```python
# Requires md or lg model (en_core_web_md / en_core_web_lg)
nlp = spacy.load("en_core_web_md")
doc1 = nlp("I like pizza")
doc2 = nlp("I love pasta")

print(doc1.similarity(doc2))        # doc-level similarity (0.0–1.0)
print(doc1[2].similarity(doc2[2]))  # token-level: "pizza" vs "pasta"

# Access raw vector
token = nlp("king")
print(token.vector)           # 300-dim numpy array
print(token.has_vector)       # True/False
print(token.vector_norm)      # L2 norm of the vector
```

### Custom Entity Rules
```python
from spacy.pipeline import EntityRuler

ruler = nlp.add_pipe("entity_ruler", before="ner")
patterns = [
    {"label": "TECH", "pattern": "spaCy"},
    {"label": "TECH", "pattern": [{"LOWER": "machine"}, {"LOWER": "learning"}]}
]
ruler.add_patterns(patterns)
```

---

## 3. Sentiment Analysis

> spaCy has no built-in sentiment scorer — use these integrations

### Option A — spaCyTextBlob
```python
# pip install spacytextblob textblob
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("spacytextblob")

doc = nlp("The movie was absolutely fantastic!")
print(doc._.blob.polarity)      # -1.0 (negative) to 1.0 (positive)
print(doc._.blob.subjectivity)  # 0.0 (objective) to 1.0 (subjective)
print(doc._.blob.sentiment_assessments.assessments)
# [('absolutely fantastic', 1.0, 1.0, None), ...]
```

### Option B — VADER (rule-based, great for social media)
```python
# pip install vaderSentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

for sent in doc.sents:                        # use spaCy for sentence splitting
    scores = analyzer.polarity_scores(sent.text)
    print(sent.text)
    print(scores)
    # {'neg': 0.0, 'neu': 0.295, 'pos': 0.705, 'compound': 0.6369}
    # compound ≥ 0.05 → positive | ≤ -0.05 → negative | else → neutral
```

### Option C — Hugging Face Transformer Pipeline
```python
# pip install transformers torch
from transformers import pipeline

sentiment = pipeline("sentiment-analysis")

for sent in doc.sents:
    result = sentiment(sent.text)[0]
    print(sent.text, "→", result["label"], f"({result['score']:.2f})")
    # "I loved it!" → POSITIVE (0.9998)
```

### Sentence Segmentation (for all sentiment options)
```python
for sent in doc.sents:
    print(sent.text)
```

---

## 4. Parsing

> Dependency parsing, sentence structure, traversal, visualization

### Dependency Parsing
```python
for token in doc:
    print(
        token.text,          # token
        token.dep_,          # dependency label
        token.head.text,     # syntactic head
        token.head.pos_,     # head POS
    )
    # "buying" → dep: ROOT, head: buying (itself)
    # "at"     → dep: prep, head: looking
```

#### Common Dependency Labels
| Label  | Meaning                        |
|--------|--------------------------------|
| ROOT   | Root of the sentence           |
| nsubj  | Nominal subject                |
| dobj   | Direct object                  |
| prep   | Prepositional modifier         |
| pobj   | Object of preposition          |
| amod   | Adjectival modifier            |
| advmod | Adverbial modifier             |
| aux    | Auxiliary verb                 |
| conj   | Conjunct                       |
| cc     | Coordinating conjunction       |

### Children & Ancestors
```python
token = doc[2]  # e.g. "looking"

print(list(token.children))    # direct syntactic children
print(list(token.ancestors))   # tokens that govern this token
print(list(token.subtree))     # full subtree rooted at token
print(list(token.lefts))       # left-side children
print(list(token.rights))      # right-side children
print(token.n_lefts)           # count of left children
print(token.n_rights)          # count of right children
```

### Subject / Object Extraction
```python
def get_subject_object(doc):
    for token in doc:
        if token.dep_ == "nsubj":
            print(f"Subject: {token.text} (head: {token.head.text})")
        if token.dep_ == "dobj":
            print(f"Object:  {token.text} (head: {token.head.text})")

get_subject_object(doc)
```

### Sentence Boundaries
```python
for sent in doc.sents:
    print(sent.text)
    print(f"  Root: {sent.root.text} [{sent.root.pos_}]")
```

### Matcher (rule-based pattern matching)
```python
from spacy.matcher import Matcher

matcher = Matcher(nlp.vocab)
pattern = [{"POS": "ADJ"}, {"POS": "NOUN"}]   # adjective followed by noun
matcher.add("ADJ_NOUN", [pattern])

matches = matcher(doc)
for match_id, start, end in matches:
    print(doc[start:end].text)   # e.g. "U.K. startup"
```

### DependencyMatcher (structural patterns)
```python
from spacy.matcher import DependencyMatcher

matcher = DependencyMatcher(nlp.vocab)
pattern = [
    {"RIGHT_ID": "verb",    "RIGHT_ATTRS": {"POS": "VERB"}},
    {"LEFT_ID": "verb",     "REL_OP": ">", "RIGHT_ID": "subject",
     "RIGHT_ATTRS": {"DEP": "nsubj"}},
    {"LEFT_ID": "verb",     "REL_OP": ">", "RIGHT_ID": "object",
     "RIGHT_ATTRS": {"DEP": "dobj"}},
]
matcher.add("SVO", [pattern])

matches = matcher(doc)
for match_id, token_ids in matches:
    subj = doc[token_ids[1]]
    verb = doc[token_ids[0]]
    obj  = doc[token_ids[2]]
    print(f"{subj} → {verb} → {obj}")
```

### Visualization
```python
from spacy import displacy

# Dependency tree (in Jupyter / browser)
displacy.render(doc, style="dep")

# Named entities
displacy.render(doc, style="ent")

# Save to HTML
html = displacy.render(doc, style="dep", page=True)
with open("parse_tree.html", "w", encoding="utf-8") as f:
    f.write(html)
```

---

## Pipeline Overview

```python
print(nlp.pipe_names)
# ['tok2vec', 'tagger', 'parser', 'ner', 'attribute_ruler', 'lemmatizer']

# Disable unused components for speed
with nlp.select_pipes(enable=["tagger", "parser"]):
    doc = nlp(text)

# Process many texts efficiently
texts = ["Text one.", "Text two.", "Text three."]
for doc in nlp.pipe(texts, batch_size=50):
    print(doc.ents)
```

---

## Model Comparison

| Model              | Size   | Vectors | Best For              |
|--------------------|--------|---------|----------------------|
| `en_core_web_sm`   | ~12 MB | ✗       | Speed, production    |
| `en_core_web_md`   | ~43 MB | ✓       | Similarity tasks     |
| `en_core_web_lg`   | ~741 MB| ✓       | Accuracy             |
| `en_core_web_trf`  | ~438 MB| ✗       | SOTA accuracy (BERT) |

```python
# Install transformer model
# pip install spacy-transformers
# python -m spacy download en_core_web_trf
```

---

## Quick Reference Card

| Task                  | Attribute / Method              |
|-----------------------|---------------------------------|
| Raw text              | `token.text`                    |
| Lowercase             | `token.lower_`                  |
| Lemma                 | `token.lemma_`                  |
| POS (coarse)          | `token.pos_`                    |
| POS (fine)            | `token.tag_`                    |
| Dependency label      | `token.dep_`                    |
| Syntactic head        | `token.head`                    |
| Named entities        | `doc.ents`                      |
| Entity label          | `ent.label_`                    |
| Noun chunks           | `doc.noun_chunks`               |
| Sentences             | `doc.sents`                     |
| Word vector           | `token.vector`                  |
| Similarity            | `doc1.similarity(doc2)`         |
| Is stop word          | `token.is_stop`                 |
| Is punctuation        | `token.is_punct`                |
| Visualize             | `displacy.render(doc)`          |
