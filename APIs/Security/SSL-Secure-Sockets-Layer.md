# SSL

An **SSL connection** (Secure Sockets Layer connection) is an encrypted communication channel between a client (like your web browser) and a server (like a website). It ensures that data transmitted between the two cannot be intercepted or read by others.

## Key Points:

**Security**: SSL encrypts data in transit, protecting sensitive information like passwords, credit card numbers, and personal data from eavesdropping or tampering.

**Authentication**: SSL certificates verify that you're connecting to the legitimate server, not an imposter.

**Visual Indicator**: When you visit a website with SSL, you'll see "https://" in the URL (instead of "http://") and often a padlock icon in your browser's address bar.

## Modern Context:

SSL has been succeeded by **TLS (Transport Layer Security)**, which is the current standard. However, people still commonly use the term "SSL" to refer to secure connections, even though they're technically using TLS. You might hear "SSL/TLS" or just "TLS" used interchangeably.

## Common Uses:
- Secure websites (online banking, shopping, email)
- Database connections
- API communications
- VPNs and other secure network connections

In the context of data engineering (like in that requirements document you have), SSL/TLS connections are important when connecting to databases, APIs, or transferring data between systems to ensure data security and compliance.

## SSL Performance Impact
**Yes, SSL/TLS does affect performance, but the impact is much smaller than most people expect.** With modern hardware and optimizations, the overhead is minimal for most use cases.

## Performance Impact - By the Numbers:

**CPU Usage**: SSL/TLS accounts for less than 1% of CPU load on modern production systems, uses less than 10KB of memory per connection, and adds less than 2% network overhead.

**Latency**: 
- The initial TLS handshake requires two extra roundtrips before the connection is established, compared to one for unencrypted HTTP
- In database performance testing with TPC-C benchmarks, enabling TLS showed only about 6% CPU increase and 1-2% difference in overall efficiency for most workloads

**Network Overhead**: For data transfer using modern encryption (AES-GCM), the overhead is approximately 29 bytes per packet, which equals about 2% overhead for large downloads.

**Real-World Example**: When Google switched Gmail to use HTTPS, it required no additional network hardware or hosts and only increased CPU load by about 1%.

## What Impacts Performance Most:

1. **Initial Handshake** - The expensive part is establishing the connection (asymmetric cryptography)
2. **Connection Type** - Short-lived connections suffer more; long-lived connections have minimal impact
3. **Session Resumption** - Reusing established sessions dramatically reduces overhead

## For AWS Glue + RDS Context:

Since Glue typically establishes long-lived database connections and processes large batches of data, the SSL overhead would be **negligible** - probably well under 5% total impact. The initial handshake happens once, then you're encrypting/decrypting data with very efficient symmetric encryption.

**Bottom line**: As CPUs continue to get faster, TLS overhead diminishes further, and the gap between secure and non-secure connections continues to shrink. The security benefits almost always outweigh the minimal performance cost.
