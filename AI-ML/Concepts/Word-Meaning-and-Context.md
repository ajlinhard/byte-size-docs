## Types of Meaning in AI/NLP

Beyond the original three, here are the key meaning types used in AI:

| Type | Description | AI Use Case |
|---|---|---|
| **Lexical** | Dictionary/word-level meaning | Spell check, glossaries |
| **Semantic** | Full interpreted meaning | Search engines, QA systems |
| **Syntactic** | Grammatical structure meaning | Parsing, grammar correction |
| **Pragmatic** | Meaning in real-world context/intent | Chatbots, intent detection |
| **Sentiment** | Emotional polarity (positive/negative) | Review analysis, social media |
| **Distributional** | Meaning from word co-occurrence | Word embeddings (Word2Vec, GloVe) |
| **Contextual** | Meaning shifts based on surrounding words | BERT, GPT, transformers |

Now let me build a full Python example covering all of these:Here's a breakdown of what the code covers across **7 meaning types**:

**1. Lexical** — Uses NLTK WordNet to fetch dictionary definitions, synsets, examples, and lemmas for a word like *"bank"* showing all its senses.

**2. Semantic** — Uses WordNet path similarity to measure how related words are (dog↔cat vs dog↔car), plus hypernyms, hyponyms, synonyms, and antonyms.

**3. Syntactic** — Uses spaCy to parse grammatical structure: Part-of-Speech tags (noun, verb, adj), dependency roles (subject, object), and named entities.

**4. Sentiment** — Uses VADER and TextBlob to detect emotional polarity (+/−/neutral) and subjectivity in text — great for reviews and social media.

**5. Distributional** — Trains a Word2Vec model to show meaning from word co-occurrence, including word similarity scores and analogies like *king − man + woman = queen*.

**6. Contextual** — Uses BERT (via `sentence-transformers`) to show how the word *"bank"* gets different vector embeddings depending on surrounding context (financial vs. river).

**7. Pragmatic** — A rule-based intent classifier that determines *what a user means to do* (greet, complain, request, thank, etc.) beyond just the literal words.

**To run it:**
```bash
pip install nltk spacy textblob gensim sentence-transformers scikit-learn
m spacy download en_core_web_sm
python nlp_meaning_types.py
```

---
## Code Examplespython -
```python
"""
=============================================================
  NLP Meaning Types in AI — Comprehensive Python Examples
  Covers: Lexical, Semantic, Syntactic, Pragmatic,
          Sentiment, Distributional, and Contextual Meaning
=============================================================

Install dependencies:
    pip install nltk spacy textblob gensim sentence-transformers
    python -m spacy download en_core_web_sm
    python -m nltk.downloader wordnet omw-1.4 vader_lexicon punkt
"""

# ─────────────────────────────────────────────
# 1. LEXICAL MEANING
#    The core dictionary definition of a word
#    Tool: NLTK WordNet
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("1️⃣  LEXICAL MEANING — WordNet Definitions")
print("="*60)

import nltk
from nltk.corpus import wordnet

nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

word = "bank"
synsets = wordnet.synsets(word)

print(f"\nWord: '{word}' has {len(synsets)} lexical senses:\n")
for i, syn in enumerate(synsets[:5], 1):
    print(f"  [{i}] Synset : {syn.name()}")
    print(f"      Definition : {syn.definition()}")
    print(f"      Examples   : {syn.examples()[:1]}")
    print(f"      Lemmas     : {[l.name() for l in syn.lemmas()]}")
    print()


# ─────────────────────────────────────────────
# 2. SEMANTIC MEANING
#    Meaning through relationships between words
#    Tool: NLTK WordNet similarity + synonyms/antonyms
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("2️⃣  SEMANTIC MEANING — Word Relationships")
print("="*60)

from nltk.corpus import wordnet as wn

word_a = wn.synset('dog.n.01')
word_b = wn.synset('cat.n.01')
word_c = wn.synset('car.n.01')

sim_ab = word_a.path_similarity(word_b)
sim_ac = word_a.path_similarity(word_c)

print(f"\n  Semantic similarity (dog ↔ cat) : {sim_ab:.4f}  ← related animals")
print(f"  Semantic similarity (dog ↔ car) : {sim_ac:.4f}  ← unrelated")

# Hyponyms and hypernyms
dog = wn.synset('dog.n.01')
print(f"\n  Hypernym of 'dog'   : {dog.hypernyms()[0].definition()}")
print(f"  Hyponym of 'dog'    : {dog.hyponyms()[0].definition()}")

# Synonyms and Antonyms
happy = wn.synsets('happy', pos=wn.ADJ)[0]
lemma = happy.lemmas()[0]
print(f"\n  Synonyms of 'happy' : {[l.name() for l in happy.lemmas()]}")
antonyms = [ant.name() for l in happy.lemmas() for ant in l.antonyms()]
print(f"  Antonyms of 'happy' : {antonyms}")


# ─────────────────────────────────────────────
# 3. SYNTACTIC MEANING
#    Meaning from grammatical structure
#    Tool: spaCy — POS tagging & dependency parsing
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("3️⃣  SYNTACTIC MEANING — POS Tags & Dependencies")
print("="*60)

import spacy

try:
    nlp = spacy.load("en_core_web_sm")

    sentences = [
        "The bank approved my loan.",
        "I sat by the river bank.",
    ]

    for sent in sentences:
        doc = nlp(sent)
        print(f"\n  Sentence: \"{sent}\"")
        print(f"  {'Token':<15} {'POS':<10} {'Dep':<15} {'Head'}")
        print(f"  {'-'*55}")
        for token in doc:
            print(f"  {token.text:<15} {token.pos_:<10} {token.dep_:<15} {token.head.text}")

        # Named entities
        if doc.ents:
            print(f"\n  Named Entities: {[(e.text, e.label_) for e in doc.ents]}")

except OSError:
    print("  ⚠️  Run: python -m spacy download en_core_web_sm")


# ─────────────────────────────────────────────
# 4. SENTIMENT MEANING
#    Emotional polarity — positive/negative/neutral
#    Tool: TextBlob + NLTK VADER
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("4️⃣  SENTIMENT MEANING — Polarity Detection")
print("="*60)

from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon', quiet=True)

sid = SentimentIntensityAnalyzer()

reviews = [
    "This product is absolutely amazing! I love it.",
    "Terrible experience. The product broke after one day.",
    "It works fine. Nothing special about it.",
]

print()
for review in reviews:
    blob = TextBlob(review)
    vader = sid.polarity_scores(review)

    polarity_label = (
        "😊 Positive" if vader['compound'] > 0.05 else
        "😞 Negative" if vader['compound'] < -0.05 else
        "😐 Neutral"
    )

    print(f"  Review : \"{review[:50]}...\"" if len(review) > 50 else f"  Review : \"{review}\"")
    print(f"  TextBlob → Polarity: {blob.sentiment.polarity:+.2f}, Subjectivity: {blob.sentiment.subjectivity:.2f}")
    print(f"  VADER   → Compound: {vader['compound']:+.2f} → {polarity_label}")
    print()


# ─────────────────────────────────────────────
# 5. DISTRIBUTIONAL MEANING
#    Meaning from word co-occurrence patterns
#    Tool: Gensim Word2Vec
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("5️⃣  DISTRIBUTIONAL MEANING — Word2Vec Embeddings")
print("="*60)

from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# Train a tiny Word2Vec model on sample sentences
corpus = [
    "the king rules the kingdom",
    "the queen rules the kingdom with grace",
    "the prince is the son of the king",
    "the princess is the daughter of the queen",
    "the doctor treats patients in the hospital",
    "the nurse helps the doctor in the hospital",
    "the teacher teaches students in the school",
    "the professor lectures students at university",
    "the dog is a loyal animal",
    "the cat is an independent animal",
    "paris is the capital of france",
    "berlin is the capital of germany",
    "london is the capital of england",
]

tokenized = [word_tokenize(s.lower()) for s in corpus]
model = Word2Vec(tokenized, vector_size=50, window=3, min_count=1, epochs=200, seed=42)

print("\n  Word2Vec trained on sample sentences.\n")

# Word similarity
pairs = [("king", "queen"), ("doctor", "nurse"), ("dog", "cat"), ("king", "dog")]
print(f"  {'Pair':<25} Similarity")
print(f"  {'-'*40}")
for w1, w2 in pairs:
    sim = model.wv.similarity(w1, w2)
    print(f"  ({w1:<10} ↔ {w2:<10})  {sim:.4f}")

# Analogy: king - man + woman = ?
print("\n  Analogy: king − man + woman ≈ ?")
try:
    result = model.wv.most_similar(positive=['king', 'woman'], negative=['man'], topn=3)
    for word, score in result:
        print(f"    → '{word}' (score: {score:.4f})")
except Exception as e:
    print(f"    (small corpus, result may vary): {e}")


# ─────────────────────────────────────────────
# 6. CONTEXTUAL MEANING
#    Meaning shifts based on surrounding context
#    Tool: sentence-transformers (BERT-based)
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("6️⃣  CONTEXTUAL MEANING — Sentence Embeddings (BERT)")
print("="*60)

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    model_bert = SentenceTransformer('all-MiniLM-L6-v2')

    # Same word "bank" in different contexts
    sentences = [
        "I deposited money at the bank.",           # financial
        "She sat by the river bank to read.",       # geographical
        "The bank approved the mortgage loan.",     # financial
        "Flowers grew along the muddy river bank.", # geographical
    ]

    embeddings = model_bert.encode(sentences)
    sim_matrix = cosine_similarity(embeddings)

    print("\n  Sentence pair similarities ('bank' in different contexts):\n")
    for i in range(len(sentences)):
        for j in range(i+1, len(sentences)):
            sim = sim_matrix[i][j]
            tag = "✅ same context" if sim > 0.7 else "❌ different context"
            print(f"  [{i+1}] vs [{j+1}]: {sim:.4f}  {tag}")
            print(f"       A: \"{sentences[i][:45]}\"")
            print(f"       B: \"{sentences[j][:45]}\"")
            print()

except ImportError:
    print("  ⚠️  Run: pip install sentence-transformers scikit-learn")


# ─────────────────────────────────────────────
# 7. PRAGMATIC MEANING
#    Meaning from intent & real-world use
#    Tool: Simple intent classifier using keywords + rules
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("7️⃣  PRAGMATIC MEANING — Intent Detection")
print("="*60)

def detect_intent(text):
    """Rule-based intent classifier (simplified NLU)."""
    text_lower = text.lower()

    intents = {
        "greeting":   ["hello", "hi", "hey", "good morning", "howdy"],
        "farewell":   ["bye", "goodbye", "see you", "farewell", "take care"],
        "question":   ["what", "how", "why", "when", "where", "who", "?"],
        "request":    ["can you", "could you", "please", "i need", "help me", "i want"],
        "complaint":  ["terrible", "broken", "awful", "hate", "worst", "disappointed"],
        "gratitude":  ["thank", "thanks", "appreciate", "grateful"],
    }

    scores = {}
    for intent, keywords in intents.items():
        scores[intent] = sum(1 for kw in keywords if kw in text_lower)

    top_intent = max(scores, key=scores.get)
    return top_intent if scores[top_intent] > 0 else "unknown"

utterances = [
    "Hello! How are you doing today?",
    "Can you please help me with my order?",
    "This is the worst service I've ever experienced!",
    "Thank you so much, that was really helpful.",
    "Goodbye, see you next time!",
    "Why is the sky blue?",
]

print()
for utt in utterances:
    intent = detect_intent(utt)
    print(f"  Text   : \"{utt}\"")
    print(f"  Intent : 🎯 {intent.upper()}")
    print()


# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("📋  SUMMARY — Meaning Types in NLP/AI")
print("="*60)

summary = [
    ("1. Lexical",       "WordNet",              "Core word definitions & senses"),
    ("2. Semantic",      "WordNet similarity",   "Word relationships & structure"),
    ("3. Syntactic",     "spaCy",                "Grammar, POS tags, dependencies"),
    ("4. Sentiment",     "VADER / TextBlob",     "Emotional polarity detection"),
    ("5. Distributional","Word2Vec (Gensim)",    "Meaning from co-occurrence"),
    ("6. Contextual",    "BERT / Transformers",  "Context-sensitive embeddings"),
    ("7. Pragmatic",     "Rule-based NLU",       "Real-world intent & use"),
]

print(f"\n  {'Type':<20} {'Tool':<25} {'Purpose'}")
print(f"  {'-'*70}")
for mtype, tool, purpose in summary:
    print(f"  {mtype:<20} {tool:<25} {purpose}")

print("\n✅ Done! All 7 meaning types demonstrated.\n")
```
