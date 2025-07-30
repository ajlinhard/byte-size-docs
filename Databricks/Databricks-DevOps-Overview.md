# Databricks DevOps Overview
In order to help with your data and dev ops Databricks has many features for assisting with CI/CD.
- IaC
- Databricks CLI
- Python SDKs and APIs
- Integration with Git Repos

## Integration with Git Repos
Let's discuss how to automate CICD with Git-based repos within Databricks. Databricks is integrated with many populatr Git Tools: Github, Azure DevOps, GitLabk, Bitbucket, AWS. In the diagram below, we show that there's a separation between the workspace within Databricks and the Git CICD system.  
<img width="1680" height="701" alt="image" src="https://github.com/user-attachments/assets/87ff54ea-0cb7-4bc2-8132-7837ac13e441" />
The Repos API provides programmatic access to Git-based repos. And with the API, you can integrate Databricks repos with your CICD workflow.

You can programmatically create, update, and delete repos, perform Git operations, and specify Git versions when running jobs based on notebooks within the repo.

**Arbitrary Files Support in Repos**
Not only that, but arbitrary files are supported within repos. This allows for portability of code for library files like Python and R. This also allows for building packages from the same repo. Plus, you can have relative imports and essentially whatever works for you.

<img width="1680" height="554" alt="image" src="https://github.com/user-attachments/assets/0fc28d45-51d0-4271-9388-ea073d50381c" />

### Git Folders
Git Folders streamlines development workflows by tightly integrating version control systems into the Databricks ecosystem, making it easier to manage code collaboratively while adhering to best practices. Some possible use cases include collaborative development for machine learning models and ETL pipelines, source-controlling SQL queries for analytics workflows, and automating deployments through CICD pipelines.  

In the GIF provided below, we show how easy it is to paste your URL from GitHub into the creation window for your Git folder. 

<img width="1672" height="1080" alt="image" src="https://github.com/user-attachments/assets/35eb017d-ecf9-4398-b115-7dabb4abe8cf" />
