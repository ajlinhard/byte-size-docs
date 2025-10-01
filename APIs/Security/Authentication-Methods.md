# API Authentication Methods
We working with APIs there is access to sensitive services, data, and networks which commonly need to be protected on both sides of the interactions. There are a couple common methods for authenticating.

### **Certificate-based Authentication**
- Uses **X.509 digital certificates** (public/private key pairs)
- The certificate is presented directly in the API call, typically via mutual TLS (mTLS)
- The server validates your certificate against its trusted certificate authority (CA)
- **Strong cryptographic proof** of identity without sending passwords
- Certificate contains identity information and is signed by a trusted CA
- Common in high-security environments, microservices, IoT devices

### **Token-based Authentication** (like JWT, OAuth access tokens, or API keys)
Intro Video: [Oathu ByteMonk](https://www.youtube.com/watch?v=ZDuRmhLSLOY)
- Uses **bearer tokens** 
- You obtain a token (usually through a login/authentication flow) and include it in request headers
- Tokens are typically time-limited and can be revoked
- Much **simpler to implement** - just include in Authorization header
- Stateless - server validates token signature without storing session data
- Most common in modern REST APIs

### **SAML-based Authentication**
Intro Videos: [SAML Intro - ByteGuru](https://www.youtube.com/watch?v=4ULlJEupV-I)
- Uses **XML-based assertions** for single sign-on (SSO)
- Involves three parties: user, identity provider (IdP), and service provider (SP)
- More of a **federated identity protocol** than direct API auth
- After SAML authentication, you typically receive a token to use for subsequent API calls
- Heavy-weight, designed for enterprise SSO scenarios
- Less common for direct API calls - more for web application SSO

**Key differences:**
- **Certificates**: "I am who I say I am because I have this cryptographic proof"
- **Tokens**: "I was authenticated earlier, here's my temporary pass"
- **SAML**: "This trusted identity provider vouches for me"

For most REST APIs today, you'll typically use **tokens** (simplest), sometimes **certificates** (highest security), and rarely SAML directly (it's usually converted to tokens).
