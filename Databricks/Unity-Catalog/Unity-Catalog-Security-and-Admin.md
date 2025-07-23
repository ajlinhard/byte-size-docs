# Unity Catalog Security and Admin
Unity Catalog stores the access control list for all the data objects in Databricks. On the backend there are other configuration and cloud features at play, such as S3 and IAM users/roles. In conjunction the cloud services + unity catalog check access, provide an audit log, and handle compute.

## Security Model
<img width="1197" height="532" alt="image" src="https://github.com/user-attachments/assets/f77169eb-ef27-4527-a523-d2bdb7906bd1" />

### Comparison of Apache Hive Metastore Security Model
Overall there is more admin work for setting up and managing the Hive MetaStoer. Examples in upper right of picture below.
<img width="1270" height="576" alt="image" src="https://github.com/user-attachments/assets/eb7daa03-5e6a-417d-acd5-90b1b3326c2a" />
