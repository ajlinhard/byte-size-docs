# Lakeflow Jobs IaC Deployments

## Deployment Steps
Here's how you typically deploy Lakeflow Declarative pipelines:

## Deployment Methods

### 1. Databricks CLI
Most common approach using the Databricks CLI:

```bash
# Install Databricks CLI
pip install databricks-cli

# Configure authentication
databricks configure --token

# Deploy pipeline
databricks pipelines deploy --file pipeline.yml --pipeline-id <pipeline-id>

# Or create new pipeline
databricks pipelines create --file pipeline.yml
```

### 2. REST API Deployment
Direct API calls for CI/CD integration:

```bash
curl -X POST \
  https://<databricks-instance>/api/2.0/pipelines \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d @pipeline.json
```

### 3. Terraform Integration
Using Databricks Terraform provider:

```hcl
resource "databricks_pipeline" "my_pipeline" {
  name = "my-lakeflow-pipeline"
  
  library {
    file {
      path = "/path/to/pipeline.yml"
    }
  }
  
  cluster {
    num_workers = 2
    spark_version = "11.3.x-scala2.12"
    node_type_id = "i3.xlarge"
  }
}
```

### 4. CI/CD Pipeline Example
GitHub Actions workflow:

```yaml
name: Deploy Lakeflow Pipeline

on:
  push:
    branches: [main]
    paths: ['pipelines/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Databricks CLI
        run: |
          pip install databricks-cli
          echo "${{ secrets.DATABRICKS_TOKEN }}" | databricks configure --token
          
      - name: Deploy Pipeline
        run: |
          databricks pipelines deploy \
            --file pipelines/my_pipeline.yml \
            --pipeline-id ${{ vars.PIPELINE_ID }}
```

## Project Structure
Typical organization for IaC deployment:

```
project/
├── pipelines/
│   ├── dev/
│   │   └── pipeline.yml
│   ├── staging/
│   │   └── pipeline.yml
│   └── prod/
│       └── pipeline.yml
├── notebooks/
│   └── data_processing.py
├── terraform/
│   └── main.tf
└── .github/
    └── workflows/
        └── deploy.yml
```

## Environment-Specific Deployment
Using parameter files for different environments:

```bash
# Deploy to dev
databricks pipelines deploy \
  --file pipeline.yml \
  --parameters-file dev_params.json

# Deploy to prod  
databricks pipelines deploy \
  --file pipeline.yml \
  --parameters-file prod_params.json
```

The key is treating your pipeline YAML/JSON files as code that gets versioned, tested, and deployed through automated processes rather than manual UI configuration.
