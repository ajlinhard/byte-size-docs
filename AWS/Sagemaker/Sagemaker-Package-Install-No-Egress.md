# Sagemaker Package Install with No Egress
## Building a Wheel File for `tiktoken` to Use in SageMaker

SageMaker often needs pre-built wheels when the instance lacks internet access or you need a specific version. Here's how to do it:

---

### Option 1: Build on a Compatible Linux Environment (Recommended)

SageMaker runs on Amazon Linux 2 / manylinux, so build the wheel on a matching architecture:

```bash
# Use a manylinux Docker container to ensure compatibility
docker run --rm -v $(pwd):/output quay.io/pypa/manylinux2014_x86_64 bash -c "
  /opt/python/cp310-cp310/bin/pip wheel tiktoken --no-deps -w /output/wheels/
"
```

This produces a `.whl` file like `tiktoken-0.x.x-cp310-cp310-manylinux...whl`.

---

### Option 2: Build Locally (if your OS matches)

```bash
pip wheel tiktoken --no-deps -w ./wheels/
```

> ⚠️ Only works reliably if you're on Linux x86_64. On Mac/Windows, use the Docker method above.

---

### Option 3: Download a Pre-built Wheel from PyPI

```bash
pip download tiktoken \
  --only-binary=:all: \
  --platform manylinux2014_x86_64 \
  --python-version 310 \
  --implementation cp \
  -d ./wheels/
```

Adjust `--python-version` to match your SageMaker Python version (e.g., `38`, `39`, `310`, `311`).

---

### Loading the Wheel into SageMaker

**1. Upload to S3:**
```bash
aws s3 cp ./wheels/ s3://your-bucket/wheels/ --recursive
```

**2. In your SageMaker notebook or training script:**
```python
import subprocess, sys

# Download from S3 first
subprocess.check_call([
    "aws", "s3", "cp",
    "s3://your-bucket/wheels/tiktoken-0.x.x-cp310-cp310-manylinux_x86_64.whl",
    "/tmp/"
])

# Install from local wheel
subprocess.check_call([
    sys.executable, "-m", "pip", "install",
    "/tmp/tiktoken-0.x.x-cp310-cp310-manylinux_x86_64.whl"
])
```

**Or via a SageMaker Estimator's `requirements.txt`** (if you bundle the wheel in your source tarball):
```
/opt/ml/code/wheels/tiktoken-0.x.x-...whl
```

---

### Tips

- **Check your Python version** in SageMaker first: `python --version`
- **tiktoken has a Rust extension** (`tiktoken_ext`), so it *must* be compiled for the target platform — pure-Python tricks won't work
- If using a **SageMaker Studio** notebook with internet access, you can just `pip install tiktoken` directly
- For **inference containers**, bundle the wheel in a custom Docker image for the cleanest solution
