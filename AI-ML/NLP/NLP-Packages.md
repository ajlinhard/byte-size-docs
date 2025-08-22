# NLP Packages
Below is a list of valuable NLP packages commonly used in the NLP world. The specific usefulness of packages may depend on use case and discpline.

- Document Indexing
  - Google Document AI
  - [Lucene (of PyLucene)](#Lucene)
- Parsing/Chunking


--
## Lucene
Lucene is a powerful, open-source full-text search library originally written in Java by Doug Cutting. It's designed to add search capabilities to applications by providing the core functionality needed to index and search large volumes of text data.

**Key aspects of Lucene:**

**Core functionality:** Lucene handles the fundamental tasks of information retrieval - it can index documents (breaking them into searchable terms), store that index efficiently, and then search through it quickly. It supports complex queries including boolean searches, phrase searches, wildcard searches, and fuzzy matching.

**Language implementations:** While the original is in Java, Lucene has been ported to other languages including Python (PyLucene), C# (Lucene.NET), and others. Each maintains the same core concepts and capabilities.

**Architecture:** Lucene works by creating inverted indexes - data structures that map each unique word to the documents containing it. This allows for very fast text searches even across millions of documents.

**Common use cases:** It's widely used in search engines, content management systems, e-commerce sites for product search, log analysis tools, and anywhere you need to search through large amounts of text data.

**Relationship to other tools:** Lucene serves as the foundation for several higher-level search platforms like Apache Solr and Elasticsearch, which build web services and additional features on top of Lucene's core search engine.

**Programming with Lucene:** Developers typically use Lucene by creating Document objects (representing the items to be searched), adding Fields to those documents, building an Index, and then using Query objects to search that index.

It's essentially the engine that powers text search in many applications you probably use daily, though it usually operates behind the scenes.
