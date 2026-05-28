## AWS Client VPN

AWS Client VPN is a managed, remote-access VPN service that lets end users securely connect to resources inside AWS (or on-premises networks) from any location using an OpenVPN-based client.

**Purpose**

It establishes an encrypted TLS tunnel between a user's device and an AWS VPC endpoint, allowing authenticated individuals to access private resources as if they were physically on the network — without exposing those resources to the public internet.

**Primary Use Cases**

- Remote workforce access to internal applications, databases, or services running in a VPC
- Secure developer access to private EC2 instances, RDS databases, or EKS clusters without a bastion host
- Contractor or third-party access with fine-grained, time-limited permissions
- Hybrid cloud access, routing traffic through AWS to reach on-premises data centers

**Related Infrastructure**

| Component | Role |
|---|---|
| **VPC & Subnets** | The network the VPN endpoint is associated with; target subnets determine which AZs are reachable |
| **Client VPN Endpoint** | The AWS-managed server-side termination point for VPN tunnels |
| **Security Groups** | Control what traffic is allowed from VPN clients once they're connected |
| **Route Tables** | Define where client traffic is directed (VPC, internet, peered VPCs, or on-prem) |
| **AWS Directory Service / Cognito / SAML IdP** | Authentication backends (Active Directory, federated SSO, or certificate-based auth) |
| **ACM (Certificate Manager)** | Stores server and optionally client certificates for mutual TLS authentication |
| **VPC Peering / Transit Gateway** | Extends VPN access beyond a single VPC to multi-VPC or multi-account architectures |
| **CloudWatch Logs** | Captures connection logs for auditing and troubleshooting |

**In short:** AWS Client VPN sits at the edge of your private network, brokering secure, identity-verified access for remote users while integrating tightly with AWS's broader networking and IAM ecosystem.

---
### SETIP INSTRUCTIONS:
 1. Make sure to **disconnect** from the Prod VPN (Open VPN)
 2. Go to AWS `va-dev` account and login
 3. Select VPC service
 4. On the left tab, select `Client VPN endpoints`
 5. On the top right, click `Client downloads` and select the one that matches your machine
    1. <img width="1510" height="883" alt="image" src="https://github.com/user-attachments/assets/4ced2279-9915-43fc-b790-4cea82f90f7a" />

 6. Go through the install steps 
 7. click on the link under `Client VPN endpoint ID`
    1. <img width="1433" height="245" alt="image" src="https://github.com/user-attachments/assets/7f0b42d2-e48e-4c7f-af99-5853c3b4a6ad" />

 8. Find AWS Client on your machine and open it 
 9. Go to File \> Manage Profiles
10. <img width="446" height="111" alt="image" src="https://github.com/user-attachments/assets/0f95a9ed-1b8d-4816-9d5a-eaded330f74c" />

11. Add the profile you downloaded 
12. You should see something like the following when successfully connected
    1. <img width="1252" height="706" alt="image" src="https://github.com/user-attachments/assets/3a0199e4-be3b-4499-bd5c-63944f6c1b67" />
13. Login to https://dev.aicessuite.com/
14. The first attempt will take some time. Try different browsers 
