# Data Engineering Vocabulary

---
# Data Description Vocabulary
When you want to talk about the different behaviors, properties, and details of data the following list is important to understand.

**For counting/quantity aspects:**
- **Multiplicity** - The number of times an element appears or how many instances exist in a relationship
- **Frequency** - How often a particular value or event occurs within a dataset
- **Magnitude** - The size or extent of a measurement, often referring to the scale of values
- **Volume** - The total amount or quantity of data, typically referring to large datasets
- **Count** - The simple numerical total of items or occurrences
- **Size** - The overall dimensions or extent of a dataset or data structure
- **Dimensionality** - The number of attributes, features, or dimensions in a dataset

**For data distribution/spread:**
- **Dispersion** - How spread out or scattered data points are from a central value
- **Variance** - A statistical measure of how much data points differ from the mean
- **Range** - The difference between the highest and lowest values in a dataset
- **Breadth** - The scope or extent of coverage across different categories or domains
- **Diversity** - The variety of different types or categories present in the data
- **Heterogeneity** - The degree to which data elements are dissimilar or varied

**For data relationships:**
- **Arity** - The number of arguments or operands a function or relation takes
- **Degree** - In graph theory, the number of connections a node has; in databases, the number of attributes in a relation
- **Valence** - The number of connections or bonds an element can form with others
- **Connectivity** - How interconnected or linked different data elements are

**For data structure properties:**
- **Cardinality** - The number of distinct elements in a set or the number of records that participate in a relationship
- **Granularity** - The level of detail or precision in data representation (fine-grained vs coarse-grained)
- **Resolution** - The degree of detail or precision available in measurements or representations
- **Density** - The ratio of actual data points to possible data points in a structure
- **Sparsity** - The degree to which a data structure contains mostly empty or zero values
- **Complexity** - The degree of intricacy or sophistication in data organization or relationships

**For uniqueness/distinctness:**
- **Distinctness** - The property of being unique or different from other elements
- **Uniqueness** - The quality of being one-of-a-kind or having no duplicates
- **Variability** - The extent to which data points differ from each other
- **Heterogeneity** - The quality of being diverse or composed of dissimilar elements

## Attributes vs Features vs Dimensions
In data science and analytics, these terms are often used interchangeably but have subtle distinctions depending on context:

**Attributes** are the most general term - they refer to any characteristic or property that describes an entity in your dataset. Every column in a database table or spreadsheet represents an attribute. For example, in a customer dataset, attributes might include name, age, income, and purchase history.

**Features** are attributes that are specifically used as input variables for machine learning models or statistical analysis. They're the measurable properties you use to make predictions or classifications. Features are often derived or engineered from raw attributes - you might combine "height" and "weight" attributes to create a "BMI" feature, or transform a "date of birth" attribute into an "age" feature.

**Dimensions** typically refer to attributes in the context of data modeling and analysis, particularly in:
- **Database design**: Dimensions are categorical attributes used for grouping and filtering (like time, geography, product category)
- **Data visualization**: Dimensions are variables you can slice and dice your data by
- **Mathematical/statistical contexts**: Dimensions refer to the number of variables or the "dimensionality" of your data space

The key distinction is that while all features are attributes, not all attributes become features. And dimensions usually emphasize the structural or categorical nature of the data rather than just any measurable property. The specific meaning often depends on whether you're doing database design, machine learning, or statistical analysis.

--
## Disparate Data
Disparate data sources refer to different, unconnected databases, systems, or repositories that store information in various formats, locations, or structures within an organization or across multiple organizations.

These sources are considered "disparate" because they:

**Exist in different locations** - data might be stored in separate departments, cloud services, on-premises servers, or third-party systems

**Use different formats** - some data might be in relational databases, others in spreadsheets, text files, APIs, or unstructured formats like documents and images

**Have different structures** - even similar data might be organized differently, use different field names, or follow different schemas

**Operate independently** - these systems often weren't designed to work together and may have been developed at different times by different teams

**Common examples include:**
- Customer information in a CRM system, financial data in an ERP system, and website analytics in Google Analytics
- Sales data in one database, inventory data in another, and customer support tickets in a third system
- Data from IoT sensors, social media platforms, and internal operational systems

The challenge with disparate data sources is that organizations often need to combine and analyze information from multiple sources to get a complete picture for decision-making. This typically requires data integration processes, ETL (Extract, Transform, Load) operations, or data warehousing solutions to bring the information together in a usable format.
