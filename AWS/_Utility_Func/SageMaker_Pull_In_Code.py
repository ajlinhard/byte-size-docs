import boto3
import os

s3 = boto3.client('s3')

# Create the directory if it doesn't exist
output_dir = "../<<New Directory - SageMaker Code Base>>"
os.makedirs(output_dir, exist_ok=True)

for fnam in [
    '<<List of Scripts>>
]:
    try:
        s3.download_file(
            Bucket = "<<Bucket Name>>",
            Key = f"scripts/{fnam}", # External Script Location
            Filename=f"{output_dir}/{fnam}"
            )
        print(f"{fnam} copied")
    except Exception as e:
        print(e)
        print(f"couldn't copy {fnam}")
