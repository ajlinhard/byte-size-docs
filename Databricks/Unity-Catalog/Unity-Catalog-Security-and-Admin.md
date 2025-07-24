# Unity Catalog Security and Admin
Unity Catalog stores the access control list for all the data objects in Databricks. On the backend there are other configuration and cloud features at play, such as S3 and IAM users/roles. In conjunction the cloud services + unity catalog check access, provide an audit log, and handle compute.

## Security Model
<img width="1197" height="532" alt="image" src="https://github.com/user-attachments/assets/f77169eb-ef27-4527-a523-d2bdb7906bd1" />

### Comparison of Apache Hive Metastore Security Model
Overall there is more admin work for setting up and managing the Hive MetaStoer. Examples in upper right of picture below.
<img width="1270" height="576" alt="image" src="https://github.com/user-attachments/assets/eb7daa03-5e6a-417d-acd5-90b1b3326c2a" />


## Privileges or Data Controls
You can grant and revokes permissions of users or groups to different data objects in the Databricks enviornment. 
- [Databricks Securable Objects](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-privileges)
- Each object type have different sets of privileges.
  - [Databricks All Privileges](https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/privileges#all-privileges)
- The creator and owner of each object automatically have owner permissions on the object.
- The user/group need access to the object and all the parent objects. Example: Tables the access is Catalog -> Schema -> Tables
- There is the reverse effect if you grant general SELECT access at the Catalog level. Then the permission pushes down automatically to all Tables.
  - [Cheatsheet of Privileges / Permissions](https://github.com/ajlinhard/byte-size-docs/blob/main/Databricks/Unity-Catalog/Unity-Catalog-Access-Patterns.md)

<img width="1287" height="565" alt="image" src="https://github.com/user-attachments/assets/c48a7f95-0c4f-40e2-a16a-8738b953cb47" />

### Access Control List
There are 3 ways to manage the access control list
1. SQL Editor with ANSI SQL grant and revoke commands
2. Catalog Explore + UI
3. Programatically with tools like Databricks CLI, Terraform, and REST APIs.
<img width="1220" height="560" alt="image" src="https://github.com/user-attachments/assets/3606a4e0-5044-4d4f-b288-00c3fe67afa8" />

## Fine-grained (Row/Column) Access Control
When it comes to fine grain access controls in a traditional database engine the normal approach is through views, but Databricks Unity Catalog takes it one step further with Row and Column security.
<img width="1221" height="564" alt="image" src="https://github.com/user-attachments/assets/17b3d6e5-c5b2-4dc9-b3ab-0a7fdb7a44ca" />

**Dynamic Views**
- Allows you to mask data columns fully or partially.
- Cherry-pick columns and rows via select-statement and where-clauses.
- Faster to implement for multi-table joins, or in scenarios where columns should not be known.

**Row and Column Security**
This is the perferred method now a days on Databricks.
- Use row filtering functions
- Use column masking functions for columns

<img width="1305" height="485" alt="image" src="https://github.com/user-attachments/assets/2ca06a0b-f3f9-4361-bf16-8287d424af28" />

