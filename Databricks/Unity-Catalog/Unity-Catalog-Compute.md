# Unity Catalog Compute
One of the powerful difference between Spark, Databricks, Snowflake, Redshift and more cloud data services is the separation of storage and compute. Learning how to setup and modulate your compute in each tool can effect your performance and cost. Therefore learning the compute options and settings in each is important. Databricks is no different!


<img width="1300" height="465" alt="image" src="https://github.com/user-attachments/assets/68bb1580-53a3-45ee-9820-ea8d0e26baf6" />

### Best Practices
- Use shared clusters as your default compute, and fall-back to single user in the case of limitations. This usually helps save on cost, but can have performance issues depending on active processing.
- Develop and Deploy using the same access model.
- The cluster types have a limit on the number of session ids per compute instance. Its over 100+, but you may hit limits if not careful.

---
## Example Compute UI Settings
### General / Cluster
<img width="1290" height="641" alt="image" src="https://github.com/user-attachments/assets/58b34e41-609e-4c32-9bbe-c13e9006544e" />

### SQL Clusters
<img width="1301" height="642" alt="image" src="https://github.com/user-attachments/assets/13c66e95-7e2c-46a3-8f8e-307c8213becb" />
