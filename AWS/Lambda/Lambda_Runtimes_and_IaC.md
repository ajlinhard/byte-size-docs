# Lambda Runtimes and IaC

---
# Lambda Runtimes
By default a lot of Lambda runtimes only include the required dependencies for boto3 to work in the runtime. So you will need to add layers and build your own Runtime.

### Documentation and Training
- [Youtube - Zip File Upload](https://www.youtube.com/watch?v=iluJFDUh-ck)
- [Youtube - Makefile and Layers](https://www.youtube.com/watch?v=j3C6iYnY-1w)


---
# Lambda IaC
When working with Lambda you can build your runtime or layer off of:
- zip files containing a prebuilt package of the code you will need.
  - The code must be structured to be
    ___| your.zip
      ___| code_file.py
      ___| other_code_folders
      ___| python
  - the python folder is where your environment packages live.
- As a container (like docker) with the per build environment and code. This can be helpful if packages are OS dependent like psycopg2.

### Example Step to making a Lambda Layer
1. Create an new folder for the code either manually or with commands.
2. On the command line making your working directory the folder.
3. Install the code into a target sub-folder called "python".
4. Zip/compress the python folder.
5. Upload to AWS to create a layer.

---
## Building Your Lambda Runtime
There are 3 main options you can use when building out the runtime of you Lambda function beyond the base runtime AWS Lambda provides:

<img width="803" height="668" alt="image" src="https://github.com/user-attachments/assets/db0efa13-06ff-4c40-9342-59842f92f81f" />
<img width="1608" height="1228" alt="image" src="https://github.com/user-attachments/assets/06b739c8-3815-4af8-8bd6-d49618c9d07c" />


Below lets break down the three Lambda deployment methods across the key criteria:

## **Complete Zip Files**

**Reliability:**
- High reliability for smaller applications (under 50MB unzipped)
- Self-contained with all dependencies bundled
- No external layer dependencies that could break
- Version management is straightforward - each deployment is atomic

**Implementation Speed:**
- Fastest to set up initially for simple functions
- Easy local testing since everything is packaged together
- Straightforward CI/CD pipeline integration
- Can become cumbersome as codebases grow larger

**Lambda Performance:**
- Good cold start performance for smaller packages
- No additional layer resolution overhead
- Direct code execution without layer mounting
- Performance degrades with larger zip files (250MB limit compressed)

## **Lambda Layers**

**Reliability:**
- Excellent for shared dependencies across multiple functions
- Risk of layer version mismatches if not managed properly
- Dependencies are centralized, reducing duplication
- Layer versioning provides good rollback capabilities

**Implementation Speed:**
- Slower initial setup due to layer creation and management
- Significantly faster subsequent deployments (only function code changes)
- Excellent for teams sharing common libraries
- Requires more sophisticated deployment orchestration

**Lambda Performance:**
- Slight cold start overhead for layer mounting
- Better performance for large shared dependencies
- Up to 5 layers per function (10GB total unzipped limit)
- Efficient memory usage when layers are shared across functions

## **Container Images**

**Reliability:**
- Highest reliability for complex applications
- Complete environment control including OS-level dependencies
- Excellent for applications with system-level requirements
- Consistent behavior between local development and Lambda

**Implementation Speed:**
- Slower initial setup requiring Docker expertise
- Longer build and deployment times
- Excellent for existing containerized applications
- More complex CI/CD pipelines but powerful for complex scenarios

**Lambda Performance:**
- Generally slower cold starts (can be 1-10 seconds for large images)
- Up to 10GB image size limit provides flexibility
- Better performance for long-running functions
- Efficient for functions requiring specific runtime environments

## **Recommendations by Use Case:**

**Use Zip Files when:**
- Simple functions with minimal dependencies
- Quick prototyping or small-scale applications
- Dependencies under 50MB total

**Use Lambda Layers when:**
- Multiple functions share common libraries
- Frequent code updates with stable dependencies
- Team collaboration with shared components

**Use Containers when:**
- Complex runtime requirements or system dependencies
- Migrating existing containerized applications
- Need for custom runtime environments
- Applications approaching zip file size limits

The choice often depends on your specific architecture, team expertise, and performance requirements. Many organizations use a hybrid approach, choosing the method that best fits each individual function's needs.
