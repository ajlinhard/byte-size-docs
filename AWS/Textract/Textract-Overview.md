# Textract Overview

### Documentation
- [AWS Developers Guide - Textract](https://docs.aws.amazon.com/textract/latest/dg/what-is.html)
- [Textract Python Examples](https://docs.aws.amazon.com/code-library/latest/ug/python_3_textract_code_examples.html)

### Limitation of Textract
AWS Textract's limited control over PDF parsing becomes apparent in several key areas:

**Page-Level Processing Control**
- You can't selectively process specific pages or page ranges efficiently
- No ability to set different extraction parameters for different sections of a document
- Can't exclude certain pages from processing to save costs
- Limited control over processing order in multi-page documents

**Text Extraction Granularity**
- No control over text segmentation - Textract decides how to break text into blocks
- Can't specify custom reading order for complex layouts
- Limited ability to preserve or ignore specific formatting (bold, italics, font sizes)
- No control over whitespace handling and normalization

**Coordinate and Layout Control**
- While Textract provides bounding boxes, you can't influence how it determines text regions
- No ability to define custom extraction zones or regions of interest
- Can't set confidence thresholds for different types of content
- Limited control over how overlapping text regions are handled

**Table and Form Processing Limitations**
- Can't define custom table detection rules or column separators
- No control over how merged cells or complex table structures are interpreted
- Form field detection logic isn't customizable - it uses ML models you can't tune
- Can't specify expected form field types or validation rules

**Output Format Constraints**
- Fixed JSON response structure - can't customize the output schema
- Limited control over how hierarchical document structure is represented
- Can't directly export to specific formats (CSV, XML) without post-processing
- Text ordering in output may not match visual reading order

**Processing Parameters**
- No control over OCR engine settings (contrast, resolution, language hints)
- Can't adjust confidence thresholds for text detection
- No ability to fine-tune the ML models for domain-specific documents
- Limited language detection controls compared to dedicated OCR solutions

**Compare this to PyMuPDF**, which gives you:
```python
# Fine-grained control examples
page = doc[page_num]  # Select specific pages
text = page.get_text("dict")  # Choose output format
blocks = page.get_text("blocks")  # Control text segmentation
images = page.get_images()  # Separate image handling

# Coordinate-based extraction
rect = fitz.Rect(x1, y1, x2, y2)
text = page.get_textbox(rect)  # Extract from specific regions

# Font and formatting control
for span in block["lines"][0]["spans"]:
    font_info = span["font"], span["size"], span["flags"]
```

This control is crucial for applications like legal document processing, financial reports, or any scenario where precise formatting preservation or custom extraction logic is needed.
