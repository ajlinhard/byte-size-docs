# Continuos Delivery and Integration (CI/CD)
This document walksthrough the process for making a system or pipeline into the modern CI/CD structure. As well as the benefits or the approach.

## Videos:
1. Helpful run quick rundown
https://www.youtube.com/watch?v=YLtlz88zrLg
2. Detailed Overview of Github Actions
https://www.youtube.com/watch?v=a5qkPEod9ng

## Docker Builds
Option 1: Command line
docker build -t book-api-test -f C:\Users\dalej\Documents\_Coding\DragonRegen\containers\book_api_server.dockerfile

Option 2: Throw github actions

## Github Documentation Help
### Understanding Github Actions
Use for basic terminology and high-level ideas for workflows: https://docs.github.com/en/actions/about-github-actions/understanding-github-actions

### Workflows: is a configurable automated process that will run one or more jobs.
- Workflow Syntax: https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions
- Resuable Workflows: https://docs.github.com/en/actions/sharing-automations/reusing-workflows
- Python Workflows Overview: https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-python

### Events: is a specific activity in a repository that triggers a workflow run.

### Jobs: is a set of steps in a workflow that is executed on the same runner. They can have dependencies on other jobs.
Steps: is either a shell script that will be executed, or an action that will be run.

### Actions: is a custom application for the GitHub Actions platform that performs a complex but frequently repeated task.
- Create/Use secrets in the actions: https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions

### Runners: is a server that runs your workflows when they're triggered. Each runner can run a single job at a time.
- Nekto Act (a local workflow runner): https://nektosact.com/usage/index.html

# Setup Steps
Here's a step-by-step process for setting up GitHub Actions to build and test a repository using Docker:

## 1. Create a GitHub Actions Workflow

1. In your repository, create a `.github/workflows` directory if it doesn't already exist[1].
2. Inside this directory, create a new file named `ci.yml` (or any other descriptive name)[1].

## 2. Define the Workflow

In the `ci.yml` file, add the following content:

```yaml
name: CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Build Docker image
      uses: docker/build-push-action@v3
      with:
        context: .
        push: false
        load: true
        tags: myapp:test
    
    - name: Run tests
      run: docker run myapp:test yarn test
```

This workflow will trigger on pushes and pull requests to the main branch[1][5].

## 3. Configure Docker

1. Ensure your repository contains a `Dockerfile` that defines how to build your application[1].
2. If your application requires multiple services, create a `docker-compose.yml` file[6].

## 4. Add Tests

1. Include test scripts in your repository, typically in a `tests` directory.
2. Ensure your `package.json` (if using Node.js) includes a `test` script[5].

## 5. Secrets Management (if needed)

1. Go to your repository settings on GitHub.
2. Navigate to "Secrets and variables" > "Actions".
3. Add any necessary secrets (e.g., Docker Hub credentials)[5].

## 6. Advanced Configuration (Optional)

- **Multi-platform builds**: Add QEMU and multi-platform support[4].
- **Caching**: Implement caching strategies to speed up builds[1].
- **Deployment**: Add steps to deploy your application after successful tests[5].

## 7. Commit and Push

1. Commit the workflow file and any other changes to your repository.
2. Push the changes to GitHub.

## 8. Monitor and Iterate

1. Go to the "Actions" tab in your GitHub repository to monitor workflow runs.
2. Review logs for any failures and iterate on your workflow as needed.

By following these steps, you'll have a basic CI pipeline that builds your Docker image, runs tests, and can be extended for more complex scenarios[1][4][5][6].

Citations:
[1] https://earthly.dev/blog/github-actions-and-docker/
[2] https://dev.to/msrabon/beginners-guide-build-push-and-deploy-docker-image-with-github-actions-aa7
[3] https://earthly.dev/blog/cicd-build-github-action-dockerhub/
[4] https://docs.docker.com/build/ci/github-actions/
[5] https://aahil13.hashnode.dev/how-to-build-a-cicd-pipeline-using-github-actions
[8] https://docs.github.com/en/actions/sharing-automations/creating-actions/creating-a-docker-container-action
[9] https://www.freecodecamp.org/news/learn-to-use-github-actions-step-by-step-guide/
[12] https://stackoverflow.com/questions/63887031/build-docker-image-locally-in-github-actions-using-docker-build-push-action
[13] https://docs.docker.com/build/ci/github-actions/test-before-push/
[14] https://github.com/docker/setup-buildx-action