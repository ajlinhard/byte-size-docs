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

---
## Users and Groups
Databricks has several types of permission groups that simplify identity management. Let me explain the different types and how to create them.
- [Databricks Identity Management](https://docs.databricks.com/aws/en/admin/users-groups/)
- [Databricks Groups](https://docs.databricks.com/aws/en/admin/users-groups/groups)
- [Databricks Managing Groups](https://docs.databricks.com/aws/en/admin/users-groups/manage-groups)

### Types of Groups in Databricks

Databricks groups are classified into four categories based on their source:

1. **Account Groups** - Created and managed at the account level
2. **External Groups** - Synced from identity providers (Microsoft Entra ID, Okta, etc.)
3. **Workspace-local Groups (Legacy)** - Created within individual workspaces
4. **Built-in Groups** - Pre-existing groups like "admins"

### How to Create Groups

#### 1. Account Groups (Recommended Approach)

**Via Account Console:**
To create account groups, you must be an account admin or workspace admin (in identity-federated workspaces):

1. As an account admin, log in to the account console
2. In the sidebar, click User management
3. On the Groups tab, click Add group
4. Enter a name for the group
5. Click Confirm
6. When prompted, add users, service principals, and groups to the group

**Via Workspace Admin Settings:**
- Navigate to workspace Settings → Identity and access → Groups
- Click "Add Group" and follow similar steps

#### 2. External Groups (Enterprise Approach)

Databricks recommends syncing groups from Microsoft Entra ID to your Azure Databricks account:

- **Automatic Identity Management (Preview)**: Enables you to add users, service principals, and groups from Microsoft Entra ID into Azure Databricks without configuring an application
- **SCIM Provisioning**: Configure enterprise application in your identity provider to sync groups

#### 3. Workspace-local Groups (Legacy)

**Via SQL Command:**
CREATE GROUP group_principal [ WITH [ USER user_principal [, ...] ] [ GROUP subgroup_principal [, ...] ] ]

Example:
```sql
-- Create an empty group
CREATE GROUP data_scientists;

-- Create group with members
CREATE GROUP analysts WITH USER `john@company.com`, `jane@company.com`;
```

**Via Terraform:**
```hcl
resource "databricks_group" "data_science" {
  display_name = "Data Science Team"
}

resource "databricks_permissions" "cluster_usage" {
  cluster_id = databricks_cluster.shared.id
  access_control {
    group_name = databricks_group.data_science.display_name
    permission_level = "CAN_MANAGE"
  }
}
```

### Group Management Permissions

To manage groups, you must have the group manager role:
- Account admins automatically have the group manager role for all groups
- Workspace admins automatically have the group manager role on groups that they create

### Best Practices

1. **Use Account Groups**: They work across workspaces and with Unity Catalog
2. **Sync from Identity Provider**: Databricks recommends syncing groups from an identity provider using a SCIM provisioning connector
3. **Avoid Workspace-local Groups**: Workspace-local groups are not synchronized to the Databricks account and are not compatible with Unity Catalog

Groups are essential for managing permissions at scale in Databricks, especially when combined with Unity Catalog's hierarchical permission model.

---
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

