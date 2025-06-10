# IAM (Identity Access Management) Overview
How we security and access to AWS infrastructure works!

## Root User
The root user needs to be protected right after setting up your account. Create an Admin user in the IAM console as soon as you can. The setup MFA for the root and Admin user.
- [Root User Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html)
- [Setting Up your AWS Account](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started-account-iam.html#create-an-admin)
- [Change Root User Password](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-password.html)

### Admin Setup
1. Login to the AWS Management Console under the root user 
2. Go to IAM via the search bar in the Console.
3. Go to create users.
4. Fill in the user name as "admin-user" or whatever you choose.
5. Go to create user group
6. The add the AdminAccess predefined policy to the group, then initialize the user group.
7. Under the next page click "add management console access"
8. Create the password for the user, or auto generate it, but SAVE the password.
9. Complete the user setup.
10. Now test you user name = "admin-user" and the password you created/generated.
[Old Example Video (IDE changed since)](https://www.youtube.com/watch?v=nIyhr4vCGuc)
