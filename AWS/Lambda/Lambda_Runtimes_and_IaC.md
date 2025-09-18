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
##Building Your Lambda Runtime
There are 3 main options you can use when building out the runtime of you Lambda function beyond the base runtime AWS Lambda provides:
I'll break down the three Lambda deployment methods across your key criteria:

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
---
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lambda Deployment Methods Comparison</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        h1 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            font-size: 2.5rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .comparison-table th {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 20px 15px;
            text-align: left;
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .comparison-table td {
            padding: 18px 15px;
            border-bottom: 1px solid #ecf0f1;
            vertical-align: top;
            line-height: 1.6;
        }
        
        .comparison-table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        .comparison-table tr:hover {
            background-color: #e8f4fd;
            transform: scale(1.01);
            transition: all 0.3s ease;
        }
        
        .metric-category {
            font-weight: bold;
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            font-size: 1.1rem;
        }
        
        .metric-subcategory {
            font-weight: 600;
            color: #2c3e50;
            background-color: #ecf0f1;
            font-style: italic;
        }
        
        .rating {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
        }
        
        .rating-excellent { color: #27ae60; }
        .rating-good { color: #2980b9; }
        .rating-moderate { color: #f39c12; }
        .rating-poor { color: #e74c3c; }
        
        .rating-icon {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-block;
        }
        
        .excellent { background-color: #27ae60; }
        .good { background-color: #2980b9; }
        .moderate { background-color: #f39c12; }
        .poor { background-color: #e74c3c; }
        
        .deployment-header {
            background: linear-gradient(135deg, #8e44ad, #9b59b6);
            color: white;
            text-align: center;
            font-size: 1.2rem;
            font-weight: 700;
        }
        
        .notes {
            background: linear-gradient(135deg, #ecf0f1, #bdc3c7);
            margin-top: 30px;
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #3498db;
        }
        
        .notes h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.4rem;
        }
        
        .notes ul {
            color: #34495e;
            line-height: 1.8;
        }
        
        .notes li {
            margin-bottom: 8px;
        }
        
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                padding: 20px;
            }
            
            .comparison-table {
                font-size: 0.9rem;
            }
            
            .comparison-table th,
            .comparison-table td {
                padding: 12px 8px;
            }
            
            h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AWS Lambda Deployment Methods Comparison</h1>
        
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th class="deployment-header">Complete Zip Files</th>
                    <th class="deployment-header">Lambda Layers</th>
                    <th class="deployment-header">Container Images</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="metric-category" colspan="4">RELIABILITY</td>
                </tr>
                <tr>
                    <td class="metric-subcategory">Dependency Management</td>
                    <td>
                        <div class="rating rating-excellent">
                            <span class="rating-icon excellent"></span>
                            Excellent
                        </div>
                        <br><small>Self-contained, no external dependencies</small>
                    </td>
                    <td>
                        <div class="rating rating-good">
                            <span class="rating-icon good"></span>
                            Good
                        </div>
                        <br><small>Risk of layer version mismatches</small>
                    </td>
                    <td>
                        <div class="rating rating-excellent">
                            <span class="rating-icon excellent"></span>
                            Excellent
                        </div>
                        <br><small>Complete environment control</small>
                    </td>
                </tr>
                <tr>
                    <td class="metric-subcategory">Version Management</td>
                    <td>
                        <div class="rating rating-excellent">
                            <span class="rating-icon excellent"></span>
                            Excellent
                        </div>
                        <br><small>Atomic deployments</small>
                    </td>
                    <td>
                        <div class="rating rating-good">
                            <span class="rating-icon good"></span>
                            Good
                        </div>
                        <br><small>Layer versioning with rollback</small>
                    </td>
                    <td>
                        <div class="rating rating-excellent">
                            <span class="rating-icon excellent"></span>
                            Excellent
                        </div>
                        <br><small>Container image versioning</small>
                    </td>
                </tr>
                <tr>
                    <td class="metric-subcategory">Production Stability</td>
                    <td>
                        <div class="rating rating-excellent">
                            <span class="rating-icon excellent"></span>
                            Excellent
                        </div>
                        <br><small>High for small apps (&lt;50MB)</small>
                    </td>
                    <td>
                        <div class="rating rating-good">
                            <span class="rating-icon good"></span>
                            Good
                        </div>
                        <br><small>Requires layer management</small>
                    </td>
                    <td>
                        <div class="rating rating-excellent">
                            <span class="rating-icon excellent"></span>
                            Excellent
                        </div>
                        <br><small>Consistent dev-prod parity</small>
                    </td>
                </tr>
                
                <tr>
                    <td class="metric-category" colspan="4">IMPLEMENTATION SPEED</td>
                </tr>
                <tr>
                    <td class="metric-subcategory">Initial Setup</td>
                    <td>
                        <div class="rating rating-excellent">
                            <span class="rating-icon excellent"></span>
                            Fastest
                        </div>
                        <br><small>Simple packaging and deployment</small>
                    </td>
                    <td>
                        <div class="rating rating-moderate">
                            <span class="rating-icon moderate"></span>
                            Moderate
                        </div>
                        <br><small>Layer creation overhead</small>
                    </td>
                    <td>
                        <div class="rating rating-poor">
                            <span class="rating-icon poor"></span>
                            Slowest
                        </div>
                        <br><small>Docker expertise required</small>
                    </td>
                </tr>
                <tr>
                    <td class="metric-subcategory">Subsequent Deployments</td>
                    <td>
                        <div class="rating rating-good">
                            <span class="rating-icon good"></span>
                            Good
                        </div>
                        <br><small>Fast for small changes</small>
                    </td>
                    <td>
                        <div class="rating rating-excellent">
                            <span class="rating-icon excellent"></span>
                            Excellent
                        </div>
                        <br><small>Only function code updates</small>
                    </td>
                    <td>
                        <div class="rating rating-moderate">
                            <span class="rating-icon moderate"></span>
                            Moderate
                        </div>
                        <br><small>Image build and push time</small>
                    </td>
                </tr>
                <tr>
                    <td class="metric-subcategory">CI/CD Integration</td>
                    <td>
                        <div class="rating rating-excellent">
                            <span class="rating-icon excellent"></span>
                            Excellent
                        </div>
                        <br><small>Straightforward pipelines</small>
                    </td>
                    <td>
                        <div class="rating rating-good">
                            <span class="rating-icon good"></span>
                            Good
                        </div>
                        <br><small>More orchestration needed</small>
                    </td>
                    <td>
                        <div class="rating rating-good">
                            <span class="rating-icon good"></span>
                            Good
                        </div>
                        <br><small>Complex but powerful</small>
                    </td>
                </tr>
                
                <tr>
                    <td class="metric-category" colspan="4">LAMBDA PERFORMANCE</td>
                </tr>
                <tr>
                    <td class="metric-subcategory">Cold Start Time</td>
                    <td>
                        <div class="rating rating-excellent">
                            <span class="rating-icon excellent"></span>
                            Excellent
                        </div>
                        <br><small>Fast for small packages</small>
                    </td>
                    <td>
                        <div class="rating rating-good">
                            <span class="rating-icon good"></span>
                            Good
                        </div>
                        <br><small>Slight layer mounting overhead</small>
                    </td>
                    <td>
                        <div class="rating rating-moderate">
                            <span class="rating-icon moderate"></span>
                            Moderate
                        </div>
                        <br><small>1-10 seconds for large images</small>
                    </td>
                </tr>
                <tr>
                    <td class="metric-subcategory">Memory Usage</td>
                    <td>
                        <div class="rating rating-good">
                            <span class="rating-icon good"></span>
                            Good
                        </div>
                        <br><small>Direct execution, no overhead</small>
                    </td>
                    <td>
                        <div class="rating rating-excellent">
                            <span class="rating-icon excellent"></span>
                            Excellent
                        </div>
                        <br><small>Shared layers across functions</small>
                    </td>
                    <td>
                        <div class="rating rating-good">
                            <span class="rating-icon good"></span>
                            Good
                        </div>
                        <br><small>Efficient for long-running</small>
                    </td>
                </tr>
                <tr>
                    <td class="metric-subcategory">Size Limits</td>
                    <td>
                        <div class="rating rating-moderate">
                            <span class="rating-icon moderate"></span>
                            Limited
                        </div>
                        <br><small>250MB compressed, 50MB unzipped</small>
                    </td>
                    <td>
                        <div class="rating rating-excellent">
                            <span class="rating-icon excellent"></span>
                            Excellent
                        </div>
                        <br><small>10GB total unzipped (5 layers)</small>
                    </td>
                    <td>
                        <div class="rating rating-excellent">
                            <span class="rating-icon excellent"></span>
                            Excellent
                        </div>
                        <br><small>Up to 10GB image size</small>
                    </td>
                </tr>
                <tr>
                    <td class="metric-subcategory">Runtime Flexibility</td>
                    <td>
                        <div class="rating rating-moderate">
                            <span class="rating-icon moderate"></span>
                            Limited
                        </div>
                        <br><small>Standard Lambda runtimes only</small>
                    </td>
                    <td>
                        <div class="rating rating-moderate">
                            <span class="rating-icon moderate"></span>
                            Limited
                        </div>
                        <br><small>Standard Lambda runtimes only</small>
                    </td>
                    <td>
                        <div class="rating rating-excellent">
                            <span class="rating-icon excellent"></span>
                            Excellent
                        </div>
                        <br><small>Custom runtime environments</small>
                    </td>
                </tr>
            </tbody>
        </table>
        
        <div class="notes">
            <h3>📋 Key Recommendations</h3>
            <ul>
                <li><strong>Use Zip Files</strong> for simple functions with minimal dependencies (&lt;50MB total)</li>
                <li><strong>Use Lambda Layers</strong> when multiple functions share common libraries or for frequent code updates</li>
                <li><strong>Use Container Images</strong> for complex applications, custom runtimes, or when migrating existing containerized apps</li>
                <li><strong>Hybrid Approach:</strong> Many organizations use different methods for different functions based on specific requirements</li>
                <li><strong>Performance Trade-off:</strong> Containers offer flexibility but have slower cold starts; Zip files are fastest for simple use cases</li>
            </ul>
        </div>
    </div>
</body>
</html>
