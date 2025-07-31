# Databricks DevOps Overview
In order to help with your data and dev ops Databricks has many features for assisting with CI/CD.
- [Databricks Asset Bundles(DABs) aka IaC](https://docs.databricks.com/aws/en/dev-tools/bundles/)
- [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/)
- [Python SDKs](https://docs.databricks.com/aws/en/dev-tools/sdk-python)
- [Databricks REST APIs](https://docs.databricks.com/api/workspace/introduction)
- Integration with Git Repos
- [Databricks Connect - For work in IDEs](https://docs.databricks.com/aws/en/dev-tools/databricks-connect/)

---
## Databricks Assets
When thinking of deploying Databricks assets, we have three different developer options. We have the REST API, the Databricks CLI, and the Databricks SDK.  
- The REST API is most flexible, but complex, and this is best for custom integrations. 
- The CLI simplifies REST API operations, but has limited flexibility.
- Finally, the SDK is the most developer-friendly and is best used for embedding Databricks functionality within applications.

<img width="1680" height="616" alt="image" src="https://github.com/user-attachments/assets/e821b682-1c94-4f85-8bc0-5fe3bee8cd47" />

### Databricks Asset Bundles (DABs)
Databricks Asset Bundles, or DABs, are designed to facilitate the adoption of best practices in software engineering, particularly for data and AI projects.  Here, we will identify four core components of software engineering practices that are supported by DABs.

<img width="1680" height="620" alt="image" src="https://github.com/user-attachments/assets/4be0dc85-a438-4b1d-96f7-2ab7f62f3c2e" />

Databricks asset bundles provide a structured approach to managing Databricks projects while adhering to software engineering best practices. By combining infrastructure as code principles with automation capabilities, they streamline collaboration, improve quality assurance, and enable efficient delivery of data-driven solutions.

DABS integrates seamlessly with Git-based workflows, enabling users to version their Databricks resources alongside source code.  By treating Databricks resources as code, DABS enables peer review through standard Git workflows like pull requests. Developers can use the Databricks  CLI with DABS to run tests on bundles and isolated environments. This ensures that workflows behave as intended.  

Finally, DABS integrates with CICD tools like GitHub Actions or Azure DevOps to automate validation, deployment, and execution on Databricks workflows.  With this foundation in place, let's take a closer look at what DABs are.  

<img width="1680" height="637" alt="image" src="https://github.com/user-attachments/assets/9f73756f-e22c-47be-b323-50f9f7e9b43a" />

If you're working locally, you build the project bundle with your team using a local environment setup.  Next, you perform a version control with your project repository where users commit changes.  Users can then manually deploy to test the changes in their development workspace instead of Databricks. When users commit changes, a notification is triggered to implement the CICD pipeline to staging and production.

<img width="1680" height="692" alt="image" src="https://github.com/user-attachments/assets/cc308126-662d-44da-bab1-a69da6a327aa" />

---
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
