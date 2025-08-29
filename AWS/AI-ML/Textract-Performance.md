# Textract Performance
AWS Textract is **primarily a per-document service** that you invoke for each individual document/image, but AWS handles some internal parallelization. Here's how it works:

## Textract Processing Model:

**1. Synchronous API (Real-time):**
```python
import boto3

textract = boto3.client('textract')

# You call this for EACH document individually
response = textract.detect_document_text(
    Document={'S3Object': {'Bucket': 'bucket', 'Name': 'document1.pdf'}}
)
```

**2. Asynchronous API (Batch):**
```python
# Start job for ONE document
job = textract.start_document_text_detection(
    DocumentLocation={'S3Object': {'Bucket': 'bucket', 'Name': 'doc1.pdf'}}
)

# Check status later
result = textract.get_document_text_detection(JobId=job['JobId'])
```

## Parallelization Patterns:

**Your responsibility to parallelize:**
- **Lambda functions**: Trigger multiple Lambdas concurrently for different PDFs
- **Step Functions**: Orchestrate parallel processing workflows
- **ECS/Batch**: Run multiple containers processing different documents
- **SQS + Workers**: Queue-based parallel processing

**Example parallel architecture:**
```python
# Using Lambda + SQS for parallel processing
import json
import boto3
from concurrent.futures import ThreadPoolExecutor

def process_pdf_batch(pdf_list):
    textract = boto3.client('textract')
    
    def process_single_pdf(pdf_path):
        return textract.start_document_text_detection(
            DocumentLocation={'S3Object': {'Bucket': 'bucket', 'Name': pdf_path}}
        )
    
    # Process multiple PDFs in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        jobs = list(executor.map(process_single_pdf, pdf_list))
    
    return jobs
```

## Textract Limitations:

**Concurrency limits:**
- **Synchronous**: 2 requests per second per account
- **Asynchronous**: 600 jobs per account (can be increased)
- **Multi-page PDFs**: Processed as single job, but AWS handles page-level parallelization internally

**Document limits:**
- **Sync API**: 5MB file size, single page
- **Async API**: 500MB file size, 3000 pages
- **Batch processing**: Must orchestrate multiple API calls yourself

## Performance Comparison:

| Approach | Parallelization | Speed | Complexity | Cost |
|----------|----------------|--------|------------|------|
| **Spark + Tika** | Native cluster parallelization | Very Fast | Low | Low |
| **Textract + Lambda** | Manual (concurrent Lambda triggers) | Fast | Medium | High |
| **Textract + Batch** | Manual (parallel jobs) | Medium | Medium | Medium |
| **Textract + Step Functions** | Orchestrated parallel execution | Medium | High | High |

## Recommended Architecture for High Volume:

```
S3 → SQS → Multiple Lambda Workers → Textract → DynamoDB
```

**Each Lambda processes one PDF:**
```python
def lambda_handler(event, context):
    # Extract PDF path from SQS message
    pdf_path = json.loads(event['Records'][0]['body'])['pdf_path']
    
    # Process single PDF with Textract
    result = textract.detect_document_text(
        Document={'S3Object': {'Bucket': 'bucket', 'Name': pdf_path}}
    )
    
    # Store results
    return result
```

## Key Takeaway:

**Textract doesn't automatically parallelize across multiple documents** - you need to architect the parallelization yourself. For high-volume PDF processing, Spark's native distributed processing is often simpler and more cost-effective than building a complex serverless architecture around Textract.

**Use Textract when:**
- You need superior OCR quality
- Processing complex layouts/forms
- Volume is moderate (hundreds to low thousands)

**Use Spark when:**
- High volume processing (thousands+)
- Text-focused extraction is sufficient
- You want simpler architecture
- Cost optimization is important
