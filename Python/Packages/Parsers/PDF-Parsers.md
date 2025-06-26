# Python PDF Parsers
Here are the most popular Python libraries for working with PDF files, along with cheatsheets and examples:

## Quick Comparison

**[PyPDF2/PyPDF4](#PyPDF2-PyPDF4)**: <br> Best for basic PDF manipulation (merging, splitting, rotating)
**[PDFplumber](#PDFplumber)**: <br> Best for text extraction and table detection from existing PDFs
**[ReportLab](#ReportLab)**: <br> Best for creating new PDFs with professional layouts

For most text extraction tasks, I'd recommend **PDFplumber** as it provides the best balance of functionality and ease of use. For creating new PDFs, **ReportLab** is the gold standard. Use **PyPDF2** when you need simple PDF manipulation operations.

# PyPDF2 / PyPDF4
A pure-python library for basic PDF operations.
# PyPDF2/PyPDF4 Cheatsheet

## Installation
```bash
pip install PyPDF2
# or for the newer version
pip install PyPDF4
```

## Basic Operations

### Reading PDFs
```python
import PyPDF2

# Open and read PDF
with open('document.pdf', 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    
    # Get number of pages
    num_pages = len(reader.pages)
    
    # Extract text from first page
    page = reader.pages[0]
    text = page.extract_text()
    
    # Extract text from all pages
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()
```

### Writing/Creating PDFs
```python
import PyPDF2

# Create a new PDF writer
writer = PyPDF2.PdfWriter()

# Add pages from existing PDF
with open('source.pdf', 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        writer.add_page(page)

# Write to new file
with open('output.pdf', 'wb') as output_file:
    writer.write(output_file)
```

### Merging PDFs
```python
import PyPDF2

merger = PyPDF2.PdfMerger()

# Add multiple PDFs
merger.append('file1.pdf')
merger.append('file2.pdf')
merger.append('file3.pdf')

# Write merged PDF
with open('merged.pdf', 'wb') as output:
    merger.write(output)

merger.close()
```

### Splitting PDFs
```python
import PyPDF2

with open('input.pdf', 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    
    # Split each page into separate file
    for i, page in enumerate(reader.pages):
        writer = PyPDF2.PdfWriter()
        writer.add_page(page)
        
        with open(f'page_{i+1}.pdf', 'wb') as output:
            writer.write(output)
```

### Password Protection
```python
import PyPDF2

# Encrypt PDF
with open('input.pdf', 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    writer = PyPDF2.PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
    
    # Add password
    writer.encrypt('password123')
    
    with open('encrypted.pdf', 'wb') as output:
        writer.write(output)

# Decrypt PDF
with open('encrypted.pdf', 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    
    if reader.is_encrypted:
        reader.decrypt('password123')
    
    # Now you can work with the PDF
    text = reader.pages[0].extract_text()
```

### Rotating Pages
```python
import PyPDF2

with open('input.pdf', 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    writer = PyPDF2.PdfWriter()
    
    for page in reader.pages:
        # Rotate 90 degrees clockwise
        rotated_page = page.rotate(90)
        writer.add_page(rotated_page)
    
    with open('rotated.pdf', 'wb') as output:
        writer.write(output)
```

## Example: Extract Text from All Pages
```python
import PyPDF2

def extract_all_text(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num, page in enumerate(reader.pages):
            text += f"--- Page {page_num + 1} ---\n"
            text += page.extract_text() + "\n\n"
    return text

# Usage
document_text = extract_all_text('my_document.pdf')
print(document_text)
```

## Limitations
- Text extraction quality varies depending on PDF structure
- Cannot extract images
- Limited formatting preservation
- Struggles with complex layouts or scanned documents

---
# PDFplumber
A more advanced library with better text extraction and table detection capabilities.# PDFplumber Cheatsheet

## Installation
```bash
pip install pdfplumber
```

## Basic Operations

### Reading and Extracting Text
```python
import pdfplumber

# Open PDF and extract text
with pdfplumber.open('document.pdf') as pdf:
    # Get first page
    first_page = pdf.pages[0]
    text = first_page.extract_text()
    
    # Extract text from all pages
    full_text = ""
    for page in pdf.pages:
        full_text += page.extract_text() + "\n"
```

### Working with Tables
```python
import pdfplumber

with pdfplumber.open('document.pdf') as pdf:
    # Extract tables from first page
    page = pdf.pages[0]
    tables = page.extract_tables()
    
    # Process each table
    for table in tables:
        for row in table:
            print(row)
    
    # Extract table as pandas DataFrame
    import pandas as pd
    if tables:
        df = pd.DataFrame(tables[0][1:], columns=tables[0][0])
        print(df)
```

### Getting Page Information
```python
import pdfplumber

with pdfplumber.open('document.pdf') as pdf:
    page = pdf.pages[0]
    
    # Page dimensions
    print(f"Width: {page.width}, Height: {page.height}")
    
    # Page metadata
    print(f"Page number: {page.page_number}")
    
    # Get all characters with positions
    chars = page.chars
    for char in chars[:5]:  # First 5 characters
        print(f"Character: '{char['text']}' at ({char['x0']}, {char['y0']})")
```

### Extracting Images
```python
import pdfplumber

with pdfplumber.open('document.pdf') as pdf:
    for page_num, page in enumerate(pdf.pages):
        # Get images on this page
        images = page.images
        
        for i, image in enumerate(images):
            print(f"Page {page_num + 1}, Image {i + 1}:")
            print(f"  Position: ({image['x0']}, {image['y0']}) to ({image['x1']}, {image['y1']})")
            print(f"  Size: {image['width']} x {image['height']}")
```

### Filtering Text by Position
```python
import pdfplumber

with pdfplumber.open('document.pdf') as pdf:
    page = pdf.pages[0]
    
    # Extract text from specific region (x0, y0, x1, y1)
    bbox = (0, 0, page.width/2, page.height/2)  # Top-left quarter
    cropped_page = page.within_bbox(bbox)
    text = cropped_page.extract_text()
    
    # Filter text by font size
    large_text = page.filter(lambda obj: obj.get('size', 0) > 12)
    large_text_content = large_text.extract_text()
```

### Working with Forms and Fields
```python
import pdfplumber

with pdfplumber.open('form.pdf') as pdf:
    page = pdf.pages[0]
    
    # Extract form fields
    # Note: pdfplumber focuses more on text/table extraction
    # For forms, consider using PyPDF2 or other specialized libraries
    
    # Get all text objects with their properties
    words = page.extract_words()
    for word in words[:5]:
        print(f"Word: '{word['text']}' Font: {word.get('fontname', 'Unknown')}")
```

## Advanced Examples

### Extract Tables with Better Control
```python
import pdfplumber
import pandas as pd

def extract_tables_advanced(pdf_path):
    tables_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # Custom table settings
            table_settings = {
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "snap_tolerance": 3,
            }
            
            tables = page.extract_tables(table_settings)
            
            for table_num, table in enumerate(tables):
                if table:  # Check if table is not empty
                    df = pd.DataFrame(table[1:], columns=table[0])
                    tables_data.append({
                        'page': page_num + 1,
                        'table': table_num + 1,
                        'data': df
                    })
    
    return tables_data

# Usage
tables = extract_tables_advanced('financial_report.pdf')
for table_info in tables:
    print(f"Page {table_info['page']}, Table {table_info['table']}:")
    print(table_info['data'].head())
    print("-" * 50)
```

### Extract Text with Formatting Information
```python
import pdfplumber

def extract_formatted_text(pdf_path):
    formatted_content = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(extra_attrs=['fontname', 'size'])
            
            for word in words:
                formatted_content.append({
                    'text': word['text'],
                    'font': word.get('fontname', ''),
                    'size': word.get('size', 0),
                    'position': (word['x0'], word['y0'])
                })
    
    return formatted_content

# Usage
content = extract_formatted_text('styled_document.pdf')
for item in content[:10]:
    print(f"'{item['text']}' - Font: {item['font']}, Size: {item['size']}")
```

### Search and Highlight Text
```python
import pdfplumber

def find_text_positions(pdf_path, search_term):
    results = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words()
            
            for word in words:
                if search_term.lower() in word['text'].lower():
                    results.append({
                        'page': page_num + 1,
                        'text': word['text'],
                        'position': (word['x0'], word['y0'], word['x1'], word['y1'])
                    })
    
    return results

# Usage
matches = find_text_positions('document.pdf', 'important')
for match in matches:
    print(f"Found '{match['text']}' on page {match['page']} at {match['position']}")
```

## Advantages
- Better text extraction than PyPDF2
- Excellent table detection and extraction
- Detailed character and word positioning
- Good handling of complex layouts
- Integrates well with pandas for data analysis

---
# ReportLab
Primarily for creating PDFs programmatically, but also useful for PDF manipulation.

# ReportLab Cheatsheet

## Installation
```bash
pip install reportlab
```

## Basic PDF Creation

### Simple Document
```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4

# Create a simple PDF
c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# Add text
c.drawString(100, height - 100, "Hello, World!")
c.drawString(100, height - 120, "This is my first PDF with ReportLab")

# Save the PDF
c.save()
```

### Working with Text
```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

c = canvas.Canvas("text_example.pdf", pagesize=A4)
width, height = A4

# Different font sizes and styles
c.setFont("Helvetica-Bold", 24)
c.drawString(50, height - 50, "Large Bold Title")

c.setFont("Helvetica", 12)
c.drawString(50, height - 80, "Regular text in Helvetica")

c.setFont("Times-Roman", 10)
c.drawString(50, height - 100, "Small text in Times Roman")

# Colored text
c.setFillColor(colors.red)
c.drawString(50, height - 120, "Red text")

c.setFillColor(colors.blue)
c.drawString(50, height - 140, "Blue text")

c.save()
```

### Shapes and Graphics
```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

c = canvas.Canvas("shapes.pdf", pagesize=A4)
width, height = A4

# Rectangle
c.setStrokeColor(colors.black)
c.setFillColor(colors.lightblue)
c.rect(50, height - 150, 200, 100, fill=1)

# Circle
c.setFillColor(colors.yellow)
c.circle(150, height - 250, 50, fill=1)

# Line
c.setStrokeColor(colors.red)
c.setLineWidth(3)
c.line(50, height - 300, 250, height - 300)

# Polygon
points = [300, height - 100, 400, height - 100, 350, height - 150]
c.setFillColor(colors.green)
c.polygon(points, fill=1)

c.save()
```

## Advanced Features

### Multi-page Document
```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def create_multipage_pdf():
    c = canvas.Canvas("multipage.pdf", pagesize=A4)
    width, height = A4
    
    # Page 1
    c.drawString(50, height - 50, "This is Page 1")
    c.drawString(50, height - 80, "Content for the first page")
    c.showPage()  # End current page and start new one
    
    # Page 2
    c.drawString(50, height - 50, "This is Page 2")
    c.drawString(50, height - 80, "Content for the second page")
    c.showPage()
    
    # Page 3
    c.drawString(50, height - 50, "This is Page 3")
    c.drawString(50, height - 80, "Final page content")
    
    c.save()

create_multipage_pdf()
```

### Tables with Platypus
```python
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def create_table_pdf():
    doc = SimpleDocTemplate("table_example.pdf", pagesize=A4)
    elements = []
    
    # Sample data
    data = [
        ['Name', 'Age', 'City', 'Salary'],
        ['John Doe', '30', 'New York', '$50,000'],
        ['Jane Smith', '25', 'Los Angeles', '$45,000'],
        ['Bob Johnson', '35', 'Chicago', '$55,000'],
        ['Alice Brown', '28', 'Houston', '$48,000']
    ]
    
    # Create table
    table = Table(data)
    
    # Apply table style
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)

create_table_pdf()
```

### Adding Images
```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

def create_pdf_with_image():
    c = canvas.Canvas("image_example.pdf", pagesize=A4)
    width, height = A4
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "PDF with Image")
    
    # Add image (you need to have an image file)
    # c.drawImage("example.jpg", 50, height - 300, width=200, height=150)
    
    # Alternative: using ImageReader for more control
    # img = ImageReader("example.jpg")
    # c.drawImage(img, 50, height - 300, width=200, height=150)
    
    c.save()

# create_pdf_with_image()
```

### Charts and Graphs
```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.lib import colors

def create_chart_pdf():
    doc = SimpleDocTemplate("chart_example.pdf", pagesize=A4)
    elements = []
    
    # Create drawing
    drawing = Drawing(400, 300)
    
    # Create bar chart
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 50
    chart.height = 200
    chart.width = 300
    
    # Chart data
    chart.data = [
        (10, 20, 30, 40),
        (15, 25, 35, 45)
    ]
    
    chart.categoryAxis.categoryNames = ['Q1', 'Q2', 'Q3', 'Q4']
    chart.bars[0].fillColor = colors.blue
    chart.bars[1].fillColor = colors.red
    
    drawing.add(chart)
    elements.append(drawing)
    
    doc.build(elements)

create_chart_pdf()
```

## Document Templates and Styles

### Using Styles
```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

def create_styled_document():
    doc = SimpleDocTemplate("styled_document.pdf", pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    title = Paragraph("My Styled Document", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Paragraph
    normal_style = styles['Normal']
    text = """
    This is a paragraph with normal styling. Lorem ipsum dolor sit amet, 
    consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore 
    et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation 
    ullamco laboris nisi ut aliquip ex ea commodo consequat.
    """
    
    para = Paragraph(text, normal_style)
    elements.append(para)
    elements.append(Spacer(1, 12))
    
    # Justified paragraph
    justified_style = ParagraphStyle(
        'Justified',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY
    )
    
    justified_para = Paragraph(text, justified_style)
    elements.append(justified_para)
    
    doc.build(elements)

create_styled_document()
```

### Complete Report Example
```python
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from datetime import datetime

def create_business_report():
    doc = SimpleDocTemplate("business_report.pdf", pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title page
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        fontSize=28,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph("Quarterly Business Report", title_style))
    elements.append(Spacer(1, 50))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(PageBreak())
    
    # Executive summary
    elements.append(Paragraph("Executive Summary", styles['Heading1']))
    elements.append(Spacer(1, 12))
    
    summary_text = """
    This report presents the quarterly performance analysis for Q4 2024. 
    Our revenue increased by 15% compared to the previous quarter, driven by 
    strong performance in our core business segments.
    """
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Financial data table
    elements.append(Paragraph("Financial Performance", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    financial_data = [
        ['Metric', 'Q3 2024', 'Q4 2024', 'Change'],
        ['Revenue', '$1.2M', '$1.38M', '+15%'],
        ['Expenses', '$800K', '$900K', '+12.5%'],
        ['Profit', '$400K', '$480K', '+20%'],
        ['Margin', '33.3%', '34.8%', '+1.5%']
    ]
    
    table = Table(financial_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    
    doc.build(elements)

create_business_report()
```

## Advantages
- Excellent for creating PDFs from scratch
- Professional-quality output
- Rich graphics and chart capabilities
- Great for reports, invoices, and documents
- Highly customizable layouts and styling

