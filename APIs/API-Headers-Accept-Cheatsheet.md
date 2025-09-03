# API Headers Accept Cheatsheet
The `Accept` header can accept multiple values! You can specify multiple media types separated by commas, and optionally include quality values (q-values) to indicate preference.

## Multiple Values Syntax

```python
headers = {
    'Accept': 'application/json, application/xml, text/html',
    # or with quality values (preference weights)
    'Accept': 'application/json;q=0.9, application/xml;q=0.8, text/html;q=0.7'
}
```

## How It's Enforced

The enforcement happens through **content negotiation** between client and server:

1. **Client sends preferences**: Your `Accept` header tells the server what formats you can handle
2. **Server evaluates**: The server looks at what it can provide vs. what you'll accept
3. **Best match selection**: Server picks the best match based on:
   - Available formats it can serve
   - Your preference order/quality values
   - Server's own preferences

## Examples

```python
# Multiple formats, server picks best available
headers = {'Accept': 'application/json, text/plain, */*'}

# With quality preferences (higher q = more preferred)
headers = {'Accept': 'application/json;q=1.0, text/xml;q=0.8, text/plain;q=0.5'}

# Specific to general fallback
headers = {'Accept': 'application/vnd.api+json, application/json, */*'}
```

## What Happens When No Match

- **406 Not Acceptable**: Server returns this if it can't provide any format you'll accept
- **Server default**: Some servers ignore `Accept` and return their default format
- **Fallback**: Using `*/*` as a fallback prevents most 406 errors


## Data Exchange & APIs
Here are the commonly used `Accept` header formats organized by use case:

**JSON APIs (most common)**
```python
'Accept': 'application/json'
'Accept': 'application/vnd.api+json'  # JSON API specification
'Accept': 'application/hal+json'      # HAL (Hypertext Application Language)
```

**XML APIs**
```python
'Accept': 'application/xml'
'Accept': 'text/xml'
'Accept': 'application/soap+xml'      # SOAP services
```

**Other structured data**
```python
'Accept': 'application/x-yaml'        # YAML
'Accept': 'text/csv'                  # CSV data
'Accept': 'application/x-msgpack'     # MessagePack
```

## File Downloads & Documents

**Documents**
```python
'Accept': 'application/pdf'           # PDF files
'Accept': 'application/msword'        # Word documents (.doc)
'Accept': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'  # .docx
'Accept': 'application/vnd.ms-excel'  # Excel files (.xls)
'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'  # .xlsx
```

**Archives & Compressed**
```python
'Accept': 'application/zip'
'Accept': 'application/gzip'
'Accept': 'application/x-tar'
'Accept': 'application/x-rar-compressed'
```

**Text Files**
```python
'Accept': 'text/plain'               # Plain text
'Accept': 'text/markdown'            # Markdown files
'Accept': 'application/rtf'          # Rich Text Format
```

## Media Content

**Images**
```python
'Accept': 'image/jpeg'
'Accept': 'image/png'
'Accept': 'image/gif'
'Accept': 'image/webp'
'Accept': 'image/svg+xml'            # SVG graphics
'Accept': 'image/*'                  # Any image format
```

**Audio/Video**
```python
'Accept': 'audio/mpeg'               # MP3
'Accept': 'audio/wav'
'Accept': 'video/mp4'
'Accept': 'video/webm'
'Accept': 'application/octet-stream' # Binary files
```

## Web Content

**HTML & Web**
```python
'Accept': 'text/html'
'Accept': 'application/xhtml+xml'
'Accept': 'text/css'
'Accept': 'application/javascript'
'Accept': 'text/javascript'
```

## Common Multi-Format Patterns

**API with fallbacks**
```python
'Accept': 'application/json, application/xml;q=0.8, text/plain;q=0.5'
```

**Web browser typical**
```python
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
```

**File upload responses**
```python
'Accept': 'application/json, text/plain'  # Success/error responses
```

**Document processing**
```python
'Accept': 'application/pdf, application/msword, text/plain'
```

**Universal fallback**
```python
'Accept': '*/*'                      # Accept anything
'Accept': 'application/json, */*'    # Prefer JSON, accept anything
```

The key is matching your `Accept` header to what the API actually serves. Many REST APIs default to JSON, but always check the API documentation for supported formats.
