# NLTK NLP Cheatsheet

> NLTK 3.x · Python 3.8+
> Install: `pip install nltk`

## Initial Setup — Download Corpora

```python
import nltk

# Download everything at once (recommended for first-time setup)
nltk.download('all')

# Or download only what you need
nltk.download('punkt')           # Tokenizers
nltk.download('punkt_tab')       # Tokenizer tables (NLTK 3.9+)
nltk.download('averaged_perceptron_tagger')  # POS tagger
nltk.download('averaged_perceptron_tagger_eng')  # POS tagger (NLTK 3.9+)
nltk.download('maxent_ne_chunker')  # NE chunker
nltk.download('maxent_ne_chunker_tab')  # NE chunker (NLTK 3.9+)
nltk.download('words')           # Word lists
nltk.download('stopwords')       # Stop word lists
nltk.download('wordnet')         # WordNet lexical database
nltk.download('vader_lexicon')   # VADER sentiment lexicon
nltk.download('omw-1.4')         # Open Multilingual WordNet
```

---

## 1. Lexical Analysis

> Tokenization, stemming, lemmatization, POS tagging, stop words, frequency

### Tokenization

```python
from nltk.tokenize import (
    word_tokenize,
    sent_tokenize,
    TweetTokenizer,
    MWETokenizer,
    RegexpTokenizer,
)

text = "Dr. Smith visited New York. He loved it!"

# Word tokenization
tokens = word_tokenize(text)
# ['Dr.', 'Smith', 'visited', 'New', 'York', '.', 'He', 'loved', 'it', '!']

# Sentence tokenization
sentences = sent_tokenize(text)
# ['Dr. Smith visited New York.', 'He loved it!']

# Tweet-aware tokenizer (handles #hashtags, @mentions, emoticons)
tweet_tok = TweetTokenizer()
tweet_tok.tokenize("I love #NLP @spaCy :)")

# Regex-based tokenizer (only alphabetic words)
reg_tok = RegexpTokenizer(r'\w+')
reg_tok.tokenize("Don't stop me now!")  # ['Don', 't', 'stop', 'me', 'now']

# Multi-word expression tokenizer
mwe_tok = MWETokenizer([('New', 'York'), ('machine', 'learning')])
mwe_tok.tokenize(word_tokenize("I study machine learning in New York"))
# ['I', 'study', 'machine_learning', 'in', 'New_York']
```

### Stop Words

```python
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))
# Also available: 'spanish', 'french', 'german', 'italian', etc.

filtered = [w for w in tokens if w.lower() not in stop_words and w.isalpha()]
```

### Stemming

```python
from nltk.stem import (
    PorterStemmer,
    SnowballStemmer,
    LancasterStemmer,
)

porter   = PorterStemmer()
snowball = SnowballStemmer("english")  # supports 15+ languages
lancaster = LancasterStemmer()         # most aggressive

words = ["running", "easily", "fairly", "studies"]
for w in words:
    print(w, porter.stem(w), snowball.stem(w), lancaster.stem(w))
# running   → run   / run   / run
# easily    → easili/ easi  / easy
# fairly    → fairli/ fair  / fair
# studies   → studi / studi / study
```

### Lemmatization

```python
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

# Default POS is noun ('n'). Specify POS for better accuracy.
# POS codes: 'n' = noun, 'v' = verb, 'a' = adjective, 'r' = adverb
lemmatizer.lemmatize("running", pos='v')   # → "run"
lemmatizer.lemmatize("better",  pos='a')   # → "good"
lemmatizer.lemmatize("studies", pos='n')   # → "study"
lemmatizer.lemmatize("went",    pos='v')   # → "go"

# Tip: use POS tags to feed the correct pos parameter
def get_wordnet_pos(treebank_tag):
    from nltk.corpus import wordnet
    if treebank_tag.startswith('J'): return wordnet.ADJ
    if treebank_tag.startswith('V'): return wordnet.VERB
    if treebank_tag.startswith('R'): return wordnet.ADV
    return wordnet.NOUN  # default

tagged = nltk.pos_tag(word_tokenize("The striped bats are hanging on their feet"))
lemmas = [lemmatizer.lemmatize(w, get_wordnet_pos(t)) for w, t in tagged]
```

### POS Tagging

```python
import nltk

tokens = word_tokenize("They refuse to permit us to obtain the refuse permit.")
tagged = nltk.pos_tag(tokens)
# [('They', 'PRP'), ('refuse', 'VBP'), ('to', 'TO'), ('permit', 'VB'), ...]

# Explain a tag
nltk.help.upenn_tagset('VBP')    # verb, present tense, not 3rd person singular
nltk.help.upenn_tagset('NNP')    # proper noun, singular
```

#### Common Penn Treebank POS Tags
| Tag   | Meaning                            |
|-------|------------------------------------|
| NN    | Noun, singular                     |
| NNS   | Noun, plural                       |
| NNP   | Proper noun, singular              |
| VB    | Verb, base form                    |
| VBD   | Verb, past tense                   |
| VBG   | Verb, gerund/present participle    |
| VBN   | Verb, past participle              |
| VBP   | Verb, non-3rd person singular      |
| VBZ   | Verb, 3rd person singular present  |
| JJ    | Adjective                          |
| RB    | Adverb                             |
| PRP   | Personal pronoun                   |
| DT    | Determiner                         |
| IN    | Preposition or subordinating conj  |
| CC    | Coordinating conjunction           |

### Frequency Distribution

```python
from nltk import FreqDist

fdist = FreqDist(tokens)
print(fdist.most_common(10))   # top 10 most frequent tokens
print(fdist['running'])        # count of a specific word
fdist.plot(20, cumulative=False)  # plot top 20 (requires matplotlib)
```

### N-Grams

```python
from nltk.util import ngrams
from nltk import bigrams, trigrams

tokens = word_tokenize("I love natural language processing")

bi  = list(bigrams(tokens))   # 2-grams
tri = list(trigrams(tokens))  # 3-grams
n4  = list(ngrams(tokens, 4)) # 4-grams

# Count bigram frequencies
fdist_bi = FreqDist(bigrams(tokens))
fdist_bi.most_common(5)
```

---

## 2. Semantic Analysis

> WordNet, synsets, similarity, named entity recognition, concordance

### WordNet — Synsets & Definitions

```python
from nltk.corpus import wordnet as wn

# Get synsets (groups of synonyms) for a word
synsets = wn.synsets("bank")
# [Synset('bank.n.01'), Synset('bank.n.02'), ..., Synset('bank.v.01'), ...]

syn = wn.synset("bank.n.01")
print(syn.definition())   # "sloping land (especially the slope beside a body of water)"
print(syn.examples())     # ["they built a wall to stop the bank from eroding"]
print(syn.lemmas())       # [Lemma('bank.n.01.bank')]
print(syn.pos())          # 'n'

# Synonyms
synonyms = set(l.name() for s in wn.synsets("happy") for l in s.lemmas())
# {'happy', 'felicitous', 'glad', 'content', ...}

# Antonyms
antonyms = set()
for syn in wn.synsets("happy"):
    for lemma in syn.lemmas():
        if lemma.antonyms():
            antonyms.add(lemma.antonyms()[0].name())
# {'unhappy', 'sad'}
```

### WordNet — Hierarchy & Relations

```python
syn = wn.synset("dog.n.01")

print(syn.hypernyms())       # more general: [Synset('canine.n.02')]
print(syn.hyponyms())        # more specific: [Synset('basenji.n.01'), ...]
print(syn.member_holonyms()) # is part of: [Synset('canis.n.01')]
print(syn.root_hypernyms())  # top of hierarchy: [Synset('entity.n.01')]
print(syn.lowest_common_hypernyms(wn.synset("cat.n.01")))
# [Synset('carnivore.n.01')]
```

### WordNet — Semantic Similarity

```python
dog  = wn.synset("dog.n.01")
cat  = wn.synset("cat.n.01")
car  = wn.synset("car.n.01")

# Path similarity (0.0–1.0, based on shortest path in hierarchy)
dog.path_similarity(cat)    # 0.2
dog.path_similarity(car)    # 0.07

# Wu-Palmer similarity (based on depth in hierarchy)
dog.wup_similarity(cat)     # 0.867
dog.wup_similarity(car)     # 0.32

# Leacock-Chodorow similarity (considers depth and path length)
dog.lch_similarity(cat)     # 2.028
```

### Named Entity Recognition (NER)

```python
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk

text = "Mark Zuckerberg founded Facebook in Cambridge, Massachusetts."
tokens = word_tokenize(text)
tagged = pos_tag(tokens)
tree   = ne_chunk(tagged)

# Extract named entities from the tree
for subtree in tree:
    if hasattr(subtree, 'label'):
        entity = " ".join([w for w, t in subtree.leaves()])
        print(f"{subtree.label()}: {entity}")
# PERSON: Mark Zuckerberg
# ORGANIZATION: Facebook
# GPE: Cambridge

# Binary mode — just marks NE vs non-NE
tree_binary = ne_chunk(tagged, binary=True)
```

#### NER Labels
| Label        | Meaning                  |
|--------------|--------------------------|
| PERSON       | People                   |
| ORGANIZATION | Companies, agencies      |
| GPE          | Geo-political entities   |
| LOCATION     | Non-GPE locations        |
| FACILITY     | Buildings, airports      |
| GSP          | Geo-social-political     |

### Concordance & Collocations

```python
from nltk.text import Text

tokens = word_tokenize(open("my_corpus.txt").read().lower())
text   = Text(tokens)

text.concordance("freedom", lines=10)    # show word in context
text.similar("freedom")                  # words used in similar contexts
text.common_contexts(["freedom", "liberty"])
text.collocations()                      # most frequent bigrams
text.dispersion_plot(["war", "freedom"]) # (requires matplotlib)
```

---

## 3. Sentiment Analysis

> VADER (built-in), SentiWordNet, custom classifiers

### VADER — Rule-Based Sentiment (Best for Social Media)

```python
from nltk.sentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

sentences = [
    "NLTK is an AMAZING library!!!",
    "This is the worst experience ever.",
    "The film was okay, nothing special.",
    "I LOVE this 😍 #awesome",
]

for s in sentences:
    scores = sia.polarity_scores(s)
    print(f"{s}")
    print(f"  neg={scores['neg']:.2f}, neu={scores['neu']:.2f}, "
          f"pos={scores['pos']:.2f}, compound={scores['compound']:.4f}")

# compound score interpretation:
# ≥  0.05 → Positive
# ≤ -0.05 → Negative
# between → Neutral

def classify(text):
    score = sia.polarity_scores(text)['compound']
    if score >= 0.05:   return "POSITIVE"
    if score <= -0.05:  return "NEGATIVE"
    return "NEUTRAL"
```

### VADER — Sentence-Level Analysis

```python
text = "The movie started slowly. But the ending was absolutely brilliant!"

for sent in sent_tokenize(text):
    scores = sia.polarity_scores(sent)
    label  = classify(sent)
    print(f"[{label}] {sent}  →  compound: {scores['compound']:.4f}")
```

### SentiWordNet — Lexicon-Based Scoring

```python
from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet as wn

# Get sentiment scores for a synset
breakdown = swn.senti_synset("outstanding.a.01")
print(breakdown.pos_score())   # 0.875 (positive)
print(breakdown.neg_score())   # 0.0
print(breakdown.obj_score())   # 0.125 (objectivity)

# Score a sentence using SentiWordNet
def swn_score(text):
    tokens = word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    pos_total = neg_total = 0

    for word, tag in tagged:
        wn_tag = get_wordnet_pos(tag)
        if wn_tag not in (wn.NOUN, wn.VERB, wn.ADJ, wn.ADV):
            continue
        synsets = list(swn.senti_synsets(word, wn_tag))
        if not synsets:
            continue
        syn = synsets[0]
        pos_total += syn.pos_score()
        neg_total += syn.neg_score()

    return pos_total, neg_total

pos, neg = swn_score("The product is outstanding but shipping was terrible.")
print(f"Positive: {pos:.2f}, Negative: {neg:.2f}")
```

### Naïve Bayes Classifier (Supervised)

```python
import random
from nltk.corpus import movie_reviews
from nltk import NaiveBayesClassifier, classify

# Prepare feature sets
def word_features(words):
    return {w: True for w in words}

documents = [
    (list(movie_reviews.words(fileid)), category)
    for category in movie_reviews.categories()
    for fileid in movie_reviews.fileids(category)
]
random.shuffle(documents)

feature_sets = [(word_features(d), c) for d, c in documents]
train_set = feature_sets[200:]
test_set  = feature_sets[:200]

# Train
classifier = NaiveBayesClassifier.train(train_set)

# Evaluate
print(classify.accuracy(classifier, test_set))        # ~0.80
classifier.show_most_informative_features(10)

# Predict
text = "The acting was brilliant and the story was gripping."
feats = word_features(word_tokenize(text.lower()))
print(classifier.classify(feats))  # "pos" or "neg"
```

---

## 4. Parsing

> CFG, RegexParser (chunking), RecursiveDescentParser, dependency-style extraction

### Context-Free Grammar (CFG) Parsing

```python
import nltk
from nltk import CFG

grammar = CFG.fromstring("""
    S   -> NP VP
    NP  -> DT NN | DT JJ NN | PRP | NNP
    VP  -> VBD NP | VBD PP | VBZ NP
    PP  -> IN NP
    DT  -> 'the' | 'a'
    NN  -> 'dog' | 'cat' | 'mat'
    NNP -> 'London'
    JJ  -> 'big' | 'small'
    VBD -> 'saw' | 'chased'
    VBZ -> 'chases'
    PRP -> 'he' | 'she'
    IN  -> 'on' | 'in'
""")

parser = nltk.ChartParser(grammar)
sentence = "the big dog chased a cat".split()

for tree in parser.parse(sentence):
    tree.pretty_print()
    print(tree)
```

### Regex Chunker (Shallow / Partial Parsing)

```python
from nltk import RegexpParser

# Chunk grammar: define phrase patterns using POS tag sequences
chunk_grammar = r"""
    NP: {<DT>?<JJ>*<NN.*>+}    # Noun phrase
    VP: {<VB.*><NP|PP>*}        # Verb phrase
    PP: {<IN><NP>}              # Prepositional phrase
"""

parser = RegexpParser(chunk_grammar)

tokens = word_tokenize("The quick brown fox jumps over the lazy dog.")
tagged = nltk.pos_tag(tokens)
tree   = parser.parse(tagged)

tree.pretty_print()            # visual parse tree

# Extract all NP chunks
for subtree in tree.subtrees(filter=lambda t: t.label() == 'NP'):
    print(" ".join(w for w, t in subtree.leaves()))
# "The quick brown fox"
# "the lazy dog"
```

### Chinking (Exclude tokens from chunks)

```python
# Chink grammar: {} removes tokens from existing chunks
chink_grammar = r"""
    NP: {<.*>+}       # Chunk everything
        }<VBD|IN>+{   # Chink (exclude) verbs and prepositions
"""

parser = RegexpParser(chink_grammar)
tree   = parser.parse(tagged)
tree.pretty_print()
```

### IOB Tags (Chunk to BIO format)

```python
from nltk.chunk import tree2conlltags

tagged = nltk.pos_tag(word_tokenize("The big cat sat on the mat."))
tree   = parser.parse(tagged)
iob    = tree2conlltags(tree)

for word, pos, iob_tag in iob:
    print(f"{word:<12} {pos:<6} {iob_tag}")
# The          DT     B-NP
# big          JJ     I-NP
# cat          NN     I-NP
# sat          VBD    O
```

### Recursive Descent Parser

```python
grammar = CFG.fromstring("""
    S  -> NP VP
    NP -> 'I' | 'the' 'dog'
    VP -> 'run' | 'see' NP
""")

rd_parser = nltk.RecursiveDescentParser(grammar)
for tree in rd_parser.parse("I see the dog".split()):
    tree.pretty_print()
```

### Shift-Reduce Parser

```python
sr_parser = nltk.ShiftReduceParser(grammar)
for tree in sr_parser.parse("I see the dog".split()):
    tree.pretty_print()
```

### Earley Chart Parser

```python
# Best for ambiguous grammars — handles all valid parses
chart_parser = nltk.EarleyChartParser(grammar)
trees = list(chart_parser.parse("I see the dog".split()))
print(f"{len(trees)} parse(s) found")
for tree in trees:
    tree.pretty_print()
```

### Probabilistic CFG (PCFG)

```python
from nltk import PCFG, ViterbiParser

pcfg = PCFG.fromstring("""
    S     -> NP VP        [1.0]
    NP    -> DT NN        [0.6]
    NP    -> NNP          [0.4]
    VP    -> VBD NP       [0.7]
    VP    -> VBD          [0.3]
    DT    -> 'the'        [1.0]
    NN    -> 'dog'        [0.5]
    NN    -> 'cat'        [0.5]
    NNP   -> 'Paris'      [1.0]
    VBD   -> 'chased'     [1.0]
""")

vp = ViterbiParser(pcfg)
for tree in vp.parse("the dog chased the cat".split()):
    print(tree)         # returns most probable parse
```

### Treebank Corpus (Pre-parsed Trees)

```python
from nltk.corpus import treebank

# Access pre-parsed sentences
tree = treebank.parsed_sents('wsj_0001.mrg')[0]
tree.pretty_print()

# Extract productions
for prod in tree.productions():
    print(prod)   # e.g. S -> NP-SBJ VP .

# Induce a PCFG from treebank
from nltk import induce_pcfg
productions = [p for sent in treebank.parsed_sents()
               for p in sent.productions()]
S = nltk.Nonterminal('S')
pcfg = induce_pcfg(S, productions)
```

### Visualize a Parse Tree

```python
tree = list(parser.parse(tagged))[0]

tree.pretty_print()          # ASCII in terminal
tree.draw()                  # GUI window (requires tkinter)

# Convert to string
print(tree.pformat())

# Access tree nodes
print(tree.label())          # root label e.g. 'S'
print(tree.leaves())         # all terminal tokens
print(tree.height())         # depth of tree
print(tree[0])               # first child subtree
print(tree[0].label())       # label of first child
```

---

## Corpus & Text Pipeline Summary

```python
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer

def nlp_pipeline(text):
    # 1. Sentence split
    sentences = sent_tokenize(text)

    # 2. Tokenize
    tokens = word_tokenize(text)

    # 3. Lowercase & remove stop words / punctuation
    stop = set(stopwords.words('english'))
    clean = [t.lower() for t in tokens if t.isalpha() and t.lower() not in stop]

    # 4. Lemmatize
    lem = WordNetLemmatizer()
    lemmas = [lem.lemmatize(t) for t in clean]

    # 5. POS tag
    tagged = nltk.pos_tag(tokens)

    # 6. NER
    ner_tree = nltk.ne_chunk(tagged)

    # 7. Sentiment
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)

    return {
        "sentences": sentences,
        "tokens": tokens,
        "clean_tokens": clean,
        "lemmas": lemmas,
        "pos_tags": tagged,
        "ner": ner_tree,
        "sentiment": sentiment,
    }

result = nlp_pipeline("Apple is hiring engineers in San Francisco. The company is doing great!")
```

---

## Quick Reference Card

| Task                    | Module / Function                            |
|-------------------------|----------------------------------------------|
| Word tokenize           | `nltk.tokenize.word_tokenize()`              |
| Sentence tokenize       | `nltk.tokenize.sent_tokenize()`              |
| Stop words              | `nltk.corpus.stopwords.words('english')`     |
| Porter stemmer          | `nltk.stem.PorterStemmer().stem()`           |
| Snowball stemmer        | `nltk.stem.SnowballStemmer(lang).stem()`     |
| Lemmatize               | `nltk.stem.WordNetLemmatizer().lemmatize()`  |
| POS tag                 | `nltk.pos_tag(tokens)`                       |
| Named entities          | `nltk.ne_chunk(tagged)`                      |
| Frequency distribution  | `nltk.FreqDist(tokens)`                      |
| N-grams                 | `nltk.ngrams(tokens, n)`                     |
| WordNet synsets         | `nltk.corpus.wordnet.synsets(word)`          |
| Word similarity         | `syn1.path_similarity(syn2)`                 |
| VADER sentiment         | `SentimentIntensityAnalyzer().polarity_scores()` |
| SentiWordNet            | `nltk.corpus.sentiwordnet.senti_synset()`    |
| Regex chunker           | `nltk.RegexpParser(grammar).parse(tagged)`   |
| CFG parser              | `nltk.ChartParser(grammar).parse(sent)`      |
| PCFG parser             | `nltk.ViterbiParser(pcfg).parse(sent)`       |
| Draw tree               | `tree.draw()`                                |
| Explain POS tag         | `nltk.help.upenn_tagset('TAG')`              |
