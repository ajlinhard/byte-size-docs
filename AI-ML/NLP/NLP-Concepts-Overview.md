# Beginner's Guide to Natural Language Processing (NLP) in Python
Natural Language Processing (NLP) is a field at the intersection of computer science, artificial intelligence, and linguistics focused on enabling computers to understand, interpret, and generate human language. This guide will introduce you to key NLP concepts and show you how to implement them in Python.

## Summary

This guide covered the foundational concepts of NLP in Python:
- Text preprocessing (tokenization, stopwords removal, stemming, lemmatization)
- Text representation (Bag of Words, TF-IDF)
- Language detection
- Part-of-speech tagging
- Named Entity Recognition
- Sentiment analysis
- Text classification
- Topic modeling
- Word embeddings
- Transformer models
- Simple chatbot implementation

## 1. Setting Up Your NLP Environment

Let's start by installing the essential libraries:

```python
# Install required libraries
pip install nltk spacy transformers scikit-learn

# Import common libraries
import nltk
import spacy
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
```

## 2. Text Preprocessing

Preprocessing is a crucial first step in any NLP pipeline:

```python
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Sample text
text = "Natural Language Processing is fascinating. It helps computers understand human language."

# Tokenization - Breaking text into words
tokens = word_tokenize(text)
print("Tokens:", tokens)

# Removing stopwords
stop_words = set(stopwords.words('english'))
filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
print("Filtered tokens:", filtered_tokens)

# Stemming - Reducing words to their root form
stemmer = PorterStemmer()
stemmed = [stemmer.stem(word) for word in filtered_tokens]
print("Stemmed words:", stemmed)

# Lemmatization - More accurate form of stemming
lemmatizer = WordNetLemmatizer()
lemmatized = [lemmatizer.lemmatize(word) for word in filtered_tokens]
print("Lemmatized words:", lemmatized)
```

## 3. Text Representation

Converting text to numerical form that machines can process:

```python
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# Sample corpus
corpus = [
    "Natural language processing is fascinating.",
    "Machine learning powers NLP systems.",
    "Python is great for NLP tasks."
]

# Bag of Words (BoW)
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(corpus)
print("Vocabulary:", vectorizer.get_feature_names_out())
print("BoW matrix shape:", X.shape)
print("BoW matrix:\n", X.toarray())

# TF-IDF (Term Frequency-Inverse Document Frequency)
tfidf_vectorizer = TfidfVectorizer()
X_tfidf = tfidf_vectorizer.fit_transform(corpus)
print("TF-IDF matrix shape:", X_tfidf.shape)
print("TF-IDF matrix:\n", X_tfidf.toarray())
```

## 4. Language Detection

Identifying the language of a text:

```python
from langdetect import detect

texts = [
    "Hello, how are you?",
    "Hola, ¿cómo estás?",
    "Bonjour, comment ça va?"
]

for text in texts:
    print(f"Text: {text}")
    print(f"Detected language: {detect(text)}")
    print()
```

## 5. Part-of-Speech Tagging

Identifying the grammatical parts of speech:

```python
import spacy

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

text = "Apple is looking at buying U.K. startup for $1 billion"
doc = nlp(text)

# Print tokens with their part-of-speech tags
for token in doc:
    print(f"{token.text}: {token.pos_} (detailed: {token.tag_})")
```

## 6. Named Entity Recognition (NER)

Identifying and classifying named entities in text:

```python
import spacy

nlp = spacy.load("en_core_web_sm")
text = "Microsoft was founded by Bill Gates and is based in Seattle, Washington."
doc = nlp(text)

print("Named Entities:")
for ent in doc.ents:
    print(f"{ent.text}: {ent.label_}")
```

## 7. Sentiment Analysis

Determining the emotional tone of text:

```python
from textblob import TextBlob

texts = [
    "I absolutely love this product! It's amazing.",
    "This was a terrible experience, I'm very disappointed.",
    "The service was okay, nothing special."
]

for text in texts:
    analysis = TextBlob(text)
    sentiment = analysis.sentiment
    print(f"Text: {text}")
    print(f"Polarity: {sentiment.polarity:.2f} (negative: -1, positive: 1)")
    print(f"Subjectivity: {sentiment.subjectivity:.2f} (objective: 0, subjective: 1)")
    print()
```

## 8. Text Classification

Categorizing text into predefined classes:

```python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report

# Example dataset (text and labels)
texts = [
    "I love this phone", "Great battery life", "Amazing camera quality",
    "Terrible customer service", "The screen broke easily", "Very disappointed",
    "Pretty average", "Not bad for the price", "Decent performance"
]

labels = ["positive", "positive", "positive", 
          "negative", "negative", "negative",
          "neutral", "neutral", "neutral"]

# Create a DataFrame
df = pd.DataFrame({'text': texts, 'sentiment': labels})

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    df['text'], df['sentiment'], test_size=0.3, random_state=42
)

# Convert text to features
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train a classifier
clf = MultinomialNB()
clf.fit(X_train_vec, y_train)

# Make predictions
y_pred = clf.predict(X_test_vec)

# Evaluate the model
print(classification_report(y_test, y_pred))
```

## 9. Topic Modeling

Discovering abstract topics in a collection of documents:

```python
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

# Sample documents
documents = [
    "The car engine makes a loud noise",
    "I love driving my new car",
    "The coffee machine is broken",
    "I like tea more than coffee",
    "The truck engine needs repair",
    "Coffee and tea are popular beverages"
]

# Convert to BoW representation
vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
X = vectorizer.fit_transform(documents)

# Apply LDA
lda = LatentDirichletAllocation(n_components=2, random_state=42)
lda.fit(X)

# Print topics
feature_names = vectorizer.get_feature_names_out()
for topic_idx, topic in enumerate(lda.components_):
    top_words_idx = topic.argsort()[:-5-1:-1]
    top_words = [feature_names[i] for i in top_words_idx]
    print(f"Topic #{topic_idx}: {' '.join(top_words)}")
```

## 10. Word Embeddings

Dense vector representations of words that capture semantic meaning:

```python
import gensim.downloader as api

# Download pre-trained word vectors
word2vec_model = api.load('word2vec-google-news-300')

# Find similar words
similar_words = word2vec_model.most_similar('computer', topn=5)
print("Words similar to 'computer':")
for word, score in similar_words:
    print(f"{word}: {score:.4f}")

# Word analogies
result = word2vec_model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
print("\nking - man + woman =", result[0][0])
```

## 11. Transformer Models

Modern deep learning architectures that have revolutionized NLP:

```python
from transformers import pipeline

# Text classification
classifier = pipeline('sentiment-analysis')
result = classifier("I've been waiting for this book for months and I'm so excited to finally read it!")
print(f"Sentiment: {result[0]['label']}, Score: {result[0]['score']:.4f}")

# Question answering
qa_pipeline = pipeline('question-answering')
context = """
Python is a high-level, interpreted programming language known for its readability.
It was created by Guido van Rossum and first released in 1991.
"""
question = "Who created Python?"
result = qa_pipeline(question=question, context=context)
print(f"Answer: {result['answer']}, Score: {result['score']:.4f}")

# Text generation
generator = pipeline('text-generation')
prompt = "Natural language processing is"
result = generator(prompt, max_length=50)
print(f"Generated text: {result[0]['generated_text']}")
```

## 12. Building a Simple Chatbot

Creating a basic rule-based chatbot:

```python
import re
import random

# Define patterns and responses
patterns = {
    r'hi|hello|hey': ['Hello!', 'Hi there!', 'Hey!'],
    r'how are you': ['I\'m good, thanks!', 'I\'m doing well. How about you?'],
    r'what is your name': ['I\'m ChatBot, a simple NLP demo.', 'You can call me ChatBot.'],
    r'bye|goodbye': ['Goodbye!', 'Bye now!', 'Talk to you later!'],
    r'.*nlp.*': ['NLP is a fascinating field!', 'Natural Language Processing is about teaching computers to understand human language.']
}

def respond(user_input):
    user_input = user_input.lower()
    for pattern, responses in patterns.items():
        if re.search(pattern, user_input):
            return random.choice(responses)
    return "I'm not sure how to respond to that."

# Example conversation
print("ChatBot: Hello! Type 'bye' to exit.")
while True:
    user_input = input("You: ")
    if user_input.lower() in ['bye', 'goodbye', 'exit']:
        print("ChatBot:", respond(user_input))
        break
    print("ChatBot:", respond(user_input))
```
