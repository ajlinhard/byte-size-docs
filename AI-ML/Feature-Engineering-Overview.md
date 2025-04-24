# Feature Engineering in NLP/AI

Feature engineering in NLP/AI refers to the process of selecting, transforming, or creating features (input variables) that help machine learning models better understand patterns in data. It's about converting raw data into a format that algorithms can effectively use.

## Why Feature Engineering Matters

Feature engineering is crucial because:
- It can significantly improve model performance
- It can reduce computational complexity
- It helps models learn meaningful patterns
- It can make models more interpretable

## Common NLP Feature Engineering Techniques

### 1. Text Preprocessing

This involves cleaning and standardizing text:

```python
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

nltk.download('stopwords')
nltk.download('wordnet')

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Tokenize
    tokens = text.split()
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # Stemming
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]
    
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]
    
    return {
        'original': text,
        'filtered': ' '.join(filtered_tokens),
        'stemmed': ' '.join(stemmed_tokens),
        'lemmatized': ' '.join(lemmatized_tokens)
    }

text = "Running quickly through the forest, she encountered 3 bears!"
results = preprocess_text(text)
print(results)
```

### 2. Bag of Words (BoW)

Represents text as word frequency counts:

```python
from sklearn.feature_extraction.text import CountVectorizer

corpus = [
    "I love machine learning",
    "I love NLP and feature engineering",
    "Feature engineering improves models"
]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(corpus)

print("Feature names:", vectorizer.get_feature_names_out())
print("BoW matrix shape:", X.shape)
print("BoW matrix:\n", X.toarray())
```

### 3. TF-IDF (Term Frequency-Inverse Document Frequency)

Weights words based on frequency in document vs. corpus:

```python
from sklearn.feature_extraction.text import TfidfVectorizer

corpus = [
    "I love machine learning",
    "I love NLP and feature engineering",
    "Feature engineering improves models"
]

tfidf_vectorizer = TfidfVectorizer()
X_tfidf = tfidf_vectorizer.fit_transform(corpus)

print("TF-IDF feature names:", tfidf_vectorizer.get_feature_names_out())
print("TF-IDF matrix shape:", X_tfidf.shape)
print("TF-IDF matrix:\n", X_tfidf.toarray())
```

### 4. N-grams

Captures sequences of words:

```python
from sklearn.feature_extraction.text import CountVectorizer

corpus = ["Natural language processing is fascinating"]

# Unigrams (single words)
unigram_vec = CountVectorizer(ngram_range=(1, 1))
# Bigrams (pairs of words)
bigram_vec = CountVectorizer(ngram_range=(2, 2))
# Trigrams (triplets of words)
trigram_vec = CountVectorizer(ngram_range=(3, 3))
# Combination of 1-3 grams
combined_vec = CountVectorizer(ngram_range=(1, 3))

X_unigram = unigram_vec.fit_transform(corpus).toarray()
X_bigram = bigram_vec.fit_transform(corpus).toarray()
X_trigram = trigram_vec.fit_transform(corpus).toarray()
X_combined = combined_vec.fit_transform(corpus).toarray()

print("Unigrams:", unigram_vec.get_feature_names_out())
print("Bigrams:", bigram_vec.get_feature_names_out())
print("Trigrams:", trigram_vec.get_feature_names_out())
print("Combined 1-3 grams:", combined_vec.get_feature_names_out())
```

### 5. Word Embeddings

Dense vector representations capturing semantic meaning:

```python
import gensim.downloader
import numpy as np

# Load pre-trained word vectors
word2vec_model = gensim.downloader.load('word2vec-google-news-300')

def text_to_vec(text, model):
    # Tokenize text
    words = text.lower().split()
    
    # Get word vectors for each word in the text
    word_vecs = [model[word] for word in words if word in model]
    
    if len(word_vecs) == 0:
        return np.zeros(model.vector_size)
    
    # Average the word vectors
    return np.mean(word_vecs, axis=0)

sentences = [
    "I love machine learning",
    "Natural language processing is fascinating"
]

for sentence in sentences:
    vec = text_to_vec(sentence, word2vec_model)
    print(f"Sentence: '{sentence}'")
    print(f"Vector shape: {vec.shape}")
    print(f"First 5 dimensions: {vec[:5]}\n")
```

### 6. Custom Features

Creating domain-specific features:

```python
import pandas as pd
import re

def extract_text_features(texts):
    features = []
    
    for text in texts:
        # Calculate basic statistics
        char_count = len(text)
        word_count = len(text.split())
        sentence_count = len(re.split(r'[.!?]+', text))
        
        # Calculate ratios and averages
        avg_word_length = char_count / max(word_count, 1)
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Count special patterns
        question_count = text.count('?')
        exclamation_count = text.count('!')
        capital_count = sum(1 for c in text if c.isupper())
        
        # Check for specific content
        contains_url = 1 if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text) else 0
        contains_email = 1 if re.search(r'[\w\.-]+@[\w\.-]+', text) else 0
        
        features.append({
            'char_count': char_count,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_word_length': avg_word_length,
            'avg_sentence_length': avg_sentence_length,
            'question_count': question_count,
            'exclamation_count': exclamation_count,
            'capital_ratio': capital_count / max(char_count, 1),
            'contains_url': contains_url,
            'contains_email': contains_email
        })
    
    return pd.DataFrame(features)

texts = [
    "Hello world! This is a test. How are you today?",
    "URGENT: Please visit https://example.com and contact us at test@example.com"
]

features_df = extract_text_features(texts)
print(features_df)
```

### 7. Feature Selection/Reduction

Selecting the most useful features:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.feature_selection import SelectKBest, chi2
import numpy as np

# Sample corpus
corpus = [
    "Machine learning is fascinating",
    "NLP is a part of machine learning",
    "Feature engineering helps improve models",
    "Deep learning models require large datasets",
    "Transformers have revolutionized NLP"
]

# Labels for feature selection
y = np.array([0, 0, 1, 1, 1])  # Binary classification example

# Create initial features
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(corpus)
feature_names = vectorizer.get_feature_names_out()

print("Original features:", X.shape)

# Method 1: Chi-square feature selection
selector = SelectKBest(chi2, k=5)
X_chi = selector.fit_transform(X, y)
selected_indices = selector.get_support(indices=True)
selected_features = [feature_names[i] for i in selected_indices]

print("Chi-square selected features:", selected_features)

# Method 2: PCA for dimension reduction
# Convert sparse to dense for PCA
X_dense = X.toarray()
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_dense)

print("PCA components shape:", X_pca.shape)
print("Explained variance ratio:", pca.explained_variance_ratio_)

# Method 3: TruncatedSVD (can work with sparse matrices)
svd = TruncatedSVD(n_components=2)
X_svd = svd.fit_transform(X)

print("SVD components shape:", X_svd.shape)
print("Explained variance ratio:", svd.explained_variance_ratio_)
```

## Advanced Feature Engineering Techniques

### 1. Contextual Embeddings (BERT, etc.)

```python
from transformers import AutoTokenizer, AutoModel
import torch

# Load pre-trained model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

def get_bert_embeddings(texts):
    # Tokenize
    encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
    
    # Get model output
    with torch.no_grad():
        outputs = model(**encoded_input)
    
    # Use the CLS token embeddings (first token of each sequence)
    embeddings = outputs.last_hidden_state[:, 0, :].numpy()
    return embeddings

texts = [
    "Natural language processing has advanced significantly.",
    "Feature engineering remains important for many applications."
]

embeddings = get_bert_embeddings(texts)
print(f"BERT embeddings shape: {embeddings.shape}")
print(f"First 5 dimensions of first text: {embeddings[0][:5]}")
```

### 2. Feature Crossing

Creating interactions between features:

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder

# Example dataset
data = {
    'text_length': [50, 120, 300, 80, 200],
    'contains_question': [1, 0, 1, 0, 1],
    'topic': ['sports', 'politics', 'technology', 'sports', 'entertainment']
}

df = pd.DataFrame(data)

# One-hot encode categorical variables
encoder = OneHotEncoder(sparse_output=False)
topic_encoded = encoder.fit_transform(df[['topic']])
topic_cols = [f"topic_{cat}" for cat in encoder.categories_[0]]

# Create DataFrame with encoded features
encoded_df = pd.DataFrame(topic_encoded, columns=topic_cols)
df = pd.concat([df.drop('topic', axis=1), encoded_df], axis=1)

# Create feature crosses
df['length_x_question'] = df['text_length'] * df['contains_question']
df['length_bin'] = pd.cut(df['text_length'], bins=[0, 100, 200, 500], labels=['short', 'medium', 'long'])

# Create interaction with categorical features
for col in topic_cols:
    df[f'length_x_{col}'] = df['text_length'] * df[col]

print(df.head())
```

## Best Practices for Feature Engineering

1. **Understand your data:** Analyze statistics, distributions, and correlations
2. **Domain knowledge is key:** Use expertise to create meaningful features
3. **Iterative process:** Test different feature sets to find what works best
4. **Avoid leakage:** Ensure features don't leak information from test data
5. **Balance complexity:** More features isn't always better (potential overfitting)
6. **Standardize/normalize:** Scale features appropriately for the algorithm
7. **Feature selection:** Remove redundant or irrelevant features

Feature engineering is both an art and a science - it requires creativity, domain knowledge, and experimental validation to determine which features work best for your specific problem.
