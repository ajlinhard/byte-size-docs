# Postgre Create and Connect
This document will walk through creating and connecting to a PostgreSQL database built on top of RDS. This is a managed version of Postgre for easier scaling and maintenance.

### Documentation
- [AWS RDS Postgre Guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ConnectToPostgreSQLInstance.html)

## Notes
- When creating a postgres database through RDS unlike local DBs the create automatically creates a KMS secret key for the password.
- Make sure you use the correct .pem file when ssh-ing in.
- Thea EC2 instance and RDS need to have the correct ports and traffic allowed by the security groups.
   - At minimum this is traffic inbound from teh EC2 instances IP on port 5432.
- When install postgres client make sure you use the correct OS command. (AMI Linux, Ubuntu, or Redshift)

## Step 1: Create RDS + Postgre
First we need to create the Postgre database itself for storing and processing data. Then we will connect to it.0
1. Go to the RDS portal in the AWS web UI
2. Click "Create Database" to begin filling out settings for the instance.
3. Complete the setting make sure to handle security correctly (likely you are not making it public.)


## Step 2: EC2 Instance for PSQL

1. Go to EC2 portal in AWS UI
2. Create an AMI instance within the same VPC as the RDS database
3. Connect to the EC2 instance
4. Install PSQL Client
```bash
sudo dnf install postgresql<version number>
```
example
```bash
sudo dnf install postgresql17.4
```

5. Connect to the database
```bash
psql \
   --host=<DB instance endpoint> \
   --port=<port> \
   --username=<master username> \
   --password \
   --dbname=<database name> 
```

```bash
psql \
   --host=progres-db-ext.cakhbszocobl.us-gov-east-1.rds.amazonaws.com \
   --port=5432 \
   --username=postgre \
   --password \
   --dbname=<database name> 
```

6. Use command line PSQL to interact
```sql
create database test_api;

CREATE TABLE claims (
    claim_id UUID PRIMARY KEY,
    is_complete BOOLEAN NOT NULL,
    ingested_timestamp TIMESTAMPTZ NOT NULL,
    completed_timestamp TIMESTAMPTZ,
    turnaround_time_minutes INTEGER,
    contentions JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

seled
```
