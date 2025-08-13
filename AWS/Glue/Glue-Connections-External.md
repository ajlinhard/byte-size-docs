# Glue External Connections
Often when working with data systems whether syncing with a legacy system or working with a local prototype, then you will need to work with external database systems. When this happens you use **JDBC (Java Database Connectivity)** as the primary technology.

## External Connections
**JDBC Connections:**
- Glue uses JDBC drivers to connect to external databases and systems
- Supports a wide range of databases including PostgreSQL, MySQL, Oracle, SQL Server, MongoDB, and many others
- You configure JDBC connection strings with hostnames, ports, credentials, and connection parameters

**Key components:**
- **Connection objects:** Store JDBC connection details in the Glue Data Catalog
- **JDBC drivers:** Glue includes many common drivers, or you can provide custom JAR files
- **Network connectivity:** Requires proper network routing (VPC, security groups, etc.)

**Common external connections:**
- On-premises databases
- Third-party cloud databases (non-AWS)
- SaaS applications with JDBC interfaces
- Custom applications exposing database endpoints

**Network considerations:**
- **VPC connectivity:** Glue jobs run in a VPC to reach external services
- **NAT Gateway/Instance:** Often needed for outbound internet connectivity
- **Direct Connect/VPN:** For secure on-premises connections
- **Security groups:** Must allow outbound traffic on appropriate ports
- **Firewall rules:** External systems must allow inbound connections from Glue

**Authentication:**
- Username/password stored securely in the connection
- Can integrate with AWS Secrets Manager for credential management
- Some drivers support other auth methods like Kerberos

The JDBC approach provides a standardized way to connect to virtually any database or system that supports JDBC connectivity, making Glue quite flexible for hybrid and multi-cloud ETL scenarios.

## Internal Cloud Connections
When connecting to AWS-hosted databases and services, AWS Glue uses **multiple technologies** depending on the specific service:

**JDBC (Most Common):**
- **Amazon RDS** (PostgreSQL, MySQL, Oracle, SQL Server, MariaDB)
- **Amazon Redshift**
- **Amazon Aurora** (PostgreSQL, MySQL)
- Uses native AWS networking within the VPC for secure, high-performance connections

**Native AWS SDK/API Integration:**
- **Amazon S3** - Uses AWS S3 APIs directly
- **Amazon DynamoDB** - Uses DynamoDB APIs and connectors
- **Amazon DocumentDB** - Can use MongoDB-compatible drivers/APIs
- **Amazon Neptune** - Uses Gremlin or SPARQL APIs for graph databases

**Specialized Connectors:**
- **Amazon OpenSearch** - Uses OpenSearch REST APIs
- **Amazon Timestream** - Uses native Timestream connectors
- **Amazon ElastiCache** - Uses Redis/Memcached protocols

**Key advantages of AWS-to-AWS connections:**
- **No internet routing** - Traffic stays within AWS backbone
- **IAM integration** - Can use IAM roles instead of username/password
- **VPC endpoints** - Private connectivity without internet gateways
- **Enhanced security** - AWS security groups and NACLs
- **Better performance** - Lower latency and higher throughput
- **Cost optimization** - No data transfer charges within the same region

**Authentication:**
- IAM roles (preferred for AWS services)
- Database authentication when required
- Integration with AWS Secrets Manager

So while JDBC is still heavily used for AWS RDS/Aurora/Redshift, Glue leverages native AWS APIs and connectors for better integration with other AWS services.

## Why are AWS-to-AWS connections Faster, over external connections?
AWS-to-AWS database connections provide significant performance advantages through several technical mechanisms:

### **Network Path Optimization:**

**Traditional Internet Routing:**
- External connections must traverse: Glue → Internet Gateway → Public Internet → ISP networks → Destination
- Multiple network hops, each adding 1-5ms latency
- Unpredictable routing through various ISPs and peering points
- Subject to internet congestion and bandwidth limitations

### **AWS Internal Routing:**
- Direct path through AWS's private backbone network
- Typically 2-3 network hops vs 8-15+ for internet routing
- Sub-millisecond latency within the same Availability Zone
- 1-2ms latency between AZs in the same region
- Dedicated, high-bandwidth fiber connections between AWS facilities

### **Bandwidth and Throughput:**

**Internet Connections:**
- Limited by NAT Gateway bandwidth (up to 45 Gbps, but shared)
- Internet Gateway throughput limits
- ISP bandwidth constraints and traffic shaping
- Variable performance based on time of day and network congestion

**AWS Internal:**
- Up to 25 Gbps network performance on larger EC2 instances (which Glue uses)
- No bandwidth charges between services in the same region
- Consistent, predictable performance
- AWS's network is designed for high-throughput data transfers

### **Protocol and Driver Optimizations:**

**JDBC over AWS Network:**
- AWS-optimized JDBC drivers for RDS/Aurora/Redshift
- Connection pooling works more efficiently with consistent low latency
- Reduced connection establishment overhead
- Better handling of large result sets due to reliable bandwidth

**Native AWS APIs:**
- S3 transfers use multipart upload/download automatically
- DynamoDB uses AWS SDK with built-in retry logic and connection optimization
- Direct API calls eliminate database protocol overhead

### **Security and Connection Overhead:**

**Internet Connections:**
- SSL/TLS encryption adds computational overhead
- Multiple certificate validations
- Potential proxy/firewall inspection delays

**AWS Internal:**
- Traffic is encrypted in transit but with less overhead
- Faster certificate validation through AWS Certificate Manager
- No intermediate proxy/inspection points

### **Real-World Performance Differences:**

**Latency Examples:**
- Same AZ: 0.1-0.5ms vs 20-50ms over internet
- Same region, different AZ: 1-2ms vs 25-75ms over internet
- Cross-region AWS: 15-150ms vs 50-300ms over internet

**Throughput Examples:**
- Large ETL job reading from RDS: 500MB/s+ vs 50-100MB/s over internet
- S3 data lake operations: Multi-GB/s vs hundreds of MB/s over internet

**Connection Pooling Benefits:**
- Internal connections can maintain larger connection pools
- Faster connection recovery after temporary failures
- More efficient resource utilization due to predictable performance

**Practical Impact on Glue Jobs:**
- **Data scanning:** 5-10x faster when reading large datasets
- **Join operations:** Reduced network wait time improves parallel processing
- **Iterative processing:** Each query cycle benefits from reduced latency
- **Error recovery:** Faster retry cycles due to reliable connectivity

This is why AWS architectures often show dramatic performance improvements when moving from hybrid (on-premises + AWS) to fully AWS-native designs.
