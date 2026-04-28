# Powershell Intro



---
## Common Permissions

```
ERROR:
npm : File C:\Program Files\nodejs\npm.ps1 cannot be loaded because running scripts is disabled on this system. For
more information, see about_Execution_Policies at https:/go.microsoft.com/fwlink/?LinkID=135170.
At line:1 char:1
+ npm --version
+ ~~~
    + CategoryInfo          : SecurityError: (:) [], PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess
```

This error is caused by **Windows PowerShell's execution policy** being set to `Restricted`, which blocks running `.ps1` scripts. When Node.js is installed on Windows, `npm` is implemented as a PowerShell script (`npm.ps1`), so PowerShell refuses to execute it.

## Fix

Run one of the following commands in **PowerShell as Administrator**:

**Option 1 – RemoteSigned (Recommended)**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
This allows locally created scripts to run, but requires remote scripts to be signed. It's the safest option.

**Option 2 – Unrestricted**
```powershell
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
```
This allows all scripts to run but is less secure.

After running either command, type `Y` to confirm, then re-run `npm --version` to verify it works.

---

**Why `-Scope CurrentUser`?** Using `CurrentUser` instead of `LocalMachine` means the change only applies to your user profile and doesn't require admin rights to set. It's also more targeted and reversible.

**Want to verify your current policy first?** Run:
```powershell
Get-ExecutionPolicy -List
```
This shows the policy at every scope so you can see exactly what's being enforced.
