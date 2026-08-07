# MASL.js Package
**MSAL** = **M**icrosoft **A**uthentication **L**ibrary. It's Microsoft's official JS SDK for handling the OIDC/OAuth dance with Entra ID from a browser app, so you don't have to hand-roll redirect logic, PKCE code generation, token parsing, and token refresh yourself. `@azure/msal-browser` is the flavor built specifically for SPAs (public clients, no secret).

## `PublicClientApplication`

This is the core object MSAL gives you to manage auth. Naming it "public" client application is MSAL explicitly encoding the concept from before — it knows this is a browser app with no secret, so internally it will always use the Authorization Code + PKCE flow rather than anything that assumes a confidential client.

## The `auth` config block

- **`clientId`** — the Application (client) ID you got back when you registered the SPA in Entra ID. This tells Entra ID which registered app is making the request.
- **`authority`** — the URL of your specific Entra tenant's login endpoint. `login.microsoftonline.com/<tenant-id>` scopes the login to *your organization's* Entra ID instance (as opposed to allowing any Microsoft account). This is where MSAL actually sends the user to authenticate.
- **`redirectUri`** — must exactly match one of the redirect URIs you registered earlier. After the user logs in at Microsoft's site, this is where they get sent back to, carrying the authorization code.

## `cache: { cacheLocation: "sessionStorage" }`

This tells MSAL where to store tokens once it has them (ID token, access token, refresh token if applicable). MSAL supports two options:

- **`localStorage`** — persists across browser tabs and even after the browser closes/reopens. More convenient (user stays logged in longer), but also means tokens sit around indefinitely and are shared across every tab.
- **`sessionStorage`** — tied to a single tab; cleared when that tab closes.

The comment explains the security tradeoff: both are readable by JavaScript running on your page, so if your app has an **XSS (cross-site scripting)** vulnerability — malicious script gets injected and runs with the same privileges as your app's own code — that script can read whatever's in storage and steal the tokens. `sessionStorage` limits the blast radius: a compromised tab only exposes that tab's tokens, and there's a smaller time window since tokens don't persist indefinitely. It's not immune to XSS (nothing JS-readable is), but it's the more conservative default MSAL's own docs recommend.

## Where this fits in the bigger federation picture

This is worth flagging because it's a subtlety in your original question about "in-app federation": this code talks **directly to Entra ID**, not to Cognito's hosted login UI. That's a specific architectural choice — instead of redirecting the user to a Cognito Hosted UI page (which itself redirects to Entra), your app handles the Entra login itself via MSAL, gets back an ID token directly from Entra, and *then* hands that token to Cognito (typically to a Cognito Identity Pool, using `CognitoIdentityClient` with the Entra ID token as the credential) to get AWS credentials.

This is what "in-app" federation means as opposed to "hosted UI" federation: the login experience stays inside your own app's UI (MSAL can do this as a popup or silent redirect within your page) rather than bouncing the user out to an AWS-branded Cognito login screen. Cognito's role shifts from "identity broker doing the OIDC handshake" to "credential vendor that trusts tokens Entra already issued directly to your app."

---
Here's the natural next step in the flow: a React app using `@azure/msal-react` (a wrapper around `msal-browser` built for React), plus how the session persists and how you'd validate the token on a Python backend.

## authConfig.js

```js
// authConfig.js
export const msalConfig = {
  auth: {
    clientId: "<entra-spa-client-id>",
    authority: "https://login.microsoftonline.com/<tenant-id>",
    redirectUri: "https://yourapp.example.com",
  },
  cache: {
    cacheLocation: "sessionStorage",
    storeAuthStateInCookie: false, // set true only if you need to support IE11/old Edge
  },
};

// Scopes for basic sign-in (identity only)
export const loginRequest = {
  scopes: ["openid", "profile", "email"],
};

// Scopes for calling YOUR OWN backend API.
// This requires a SEPARATE App Registration in Entra ID for the API itself
// (Platform = "Web" or none, with an exposed scope like "access_as_user"),
// distinct from the SPA registration.
export const apiRequest = {
  scopes: ["api://<your-api-client-id>/access_as_user"],
};
```

That `apiRequest` scope is important and easy to miss: an access token minted for Microsoft Graph (the default if you only request `openid`/`profile`/`email`) has an **audience** of Graph, not your API. Your Python backend will reject it. Your backend needs its own App Registration in Entra ID so tokens can be minted with *it* as the audience.

## App.jsx

```jsx
// App.jsx
import React from "react";
import { PublicClientApplication, EventType } from "@azure/msal-browser";
import { MsalProvider, useMsal, useIsAuthenticated } from "@azure/msal-react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { msalConfig, loginRequest } from "./authConfig";
import Dashboard from "./Dashboard";

const msalInstance = new PublicClientApplication(msalConfig);

// Restore any existing session on load (handles redirect responses too)
msalInstance.initialize().then(() => {
  msalInstance.handleRedirectPromise();

  // Auto-select the first account if one exists in cache (e.g. after refresh)
  const accounts = msalInstance.getAllAccounts();
  if (accounts.length > 0) {
    msalInstance.setActiveAccount(accounts[0]);
  }

  msalInstance.addEventCallback((event) => {
    if (event.eventType === EventType.LOGIN_SUCCESS && event.payload.account) {
      msalInstance.setActiveAccount(event.payload.account);
    }
  });
});

function LoginButton() {
  const { instance } = useMsal();
  return (
    <button onClick={() => instance.loginRedirect(loginRequest)}>
      Sign in with Microsoft
    </button>
  );
}

function ProtectedRoute({ children }) {
  const isAuthenticated = useIsAuthenticated();
  return isAuthenticated ? children : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <MsalProvider instance={msalInstance}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LoginButton />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </MsalProvider>
  );
}
```

## How the user stays authenticated across pages

Two different things are happening, worth separating:

**Within the same tab, navigating routes:** Because this is a SPA, `msalInstance` is a JS object living in memory for as long as the tab is open — React Router swapping pages doesn't reload the browser, so nothing resets. `useIsAuthenticated()` and `useMsal()` just read from that live instance. No extra work needed here.

**After a hard refresh, or opening a new tab:** The in-memory object is gone, but MSAL rebuilds it from `sessionStorage`. On `msalInstance.initialize()`, MSAL checks the cache for tokens and a refresh token. If the access/ID token has expired, MSAL silently uses the refresh token (via a hidden iframe or direct token endpoint call — no visible redirect) to get new ones. The user doesn't notice a thing unless the refresh token itself is expired or revoked (e.g., admin forced sign-out, conditional access policy triggered), in which case MSAL falls back to an interactive login.

Note `sessionStorage` means a *new tab* won't inherit the session automatically (each tab is isolated) — that's the tradeoff for the XSS protection mentioned earlier. If you want sign-in to persist across tabs/browser restarts, that's `localStorage`, at the cost of a larger XSS blast radius.

## Calling the Python backend

Before every API call, acquire a token silently and attach it:

```js
// apiClient.js
import axios from "axios";
import { msalInstance } from "./App";
import { apiRequest } from "./authConfig";

const apiClient = axios.create({ baseURL: "https://api.yourapp.example.com" });

apiClient.interceptors.request.use(async (config) => {
  const account = msalInstance.getActiveAccount();
  if (!account) throw new Error("No active account — user not signed in");

  const result = await msalInstance.acquireTokenSilent({
    ...apiRequest,
    account,
  });

  config.headers.Authorization = `Bearer ${result.accessToken}`;
  return config;
});

export default apiClient;
```

`acquireTokenSilent` returns the cached token if it's still valid, silently refreshes it if it's expired but the refresh token is good, and only throws (requiring you to catch it and call `acquireTokenRedirect`/`acquireTokenPopup`) if interactive login is truly unavoidable.

## Validating the token on the Python backend

The backend never talks to Cognito or MSAL — it just verifies the JWT it receives is a legitimately signed Entra ID token, meant for it specifically. FastAPI example using `PyJWT`:

```python
# auth.py
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, Header

TENANT_ID = "<tenant-id>"
API_CLIENT_ID = "<your-api-client-id>"  # the API's own App Registration ID
ISSUER = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0"
JWKS_URL = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"

jwks_client = PyJWKClient(JWKS_URL)  # handles fetching + caching Entra's signing keys

def verify_token(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ")

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=API_CLIENT_ID,
            issuer=ISSUER,
        )
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    return claims  # contains sub, name, email/preferred_username, etc.
```

```python
# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from auth import verify_token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourapp.example.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/me")
def read_current_user(user=Depends(verify_token)):
    return {"email": user.get("preferred_username"), "name": user.get("name")}
```

`PyJWKClient` fetches and caches Entra ID's public signing keys from the JWKS endpoint, so `jwt.decode` can verify the token's signature without you managing key rotation yourself. The `audience` and `issuer` checks are what enforce that this token was actually minted for *your* API by *your* tenant — without them, any valid Entra token from anywhere would pass.

One architectural note worth flagging: this Python-backend validation is **separate and parallel** to the Cognito Identity Pool piece from earlier. Cognito is for getting temporary *AWS* credentials to call AWS services directly from the browser. Your own Python API doesn't go through Cognito at all — it just trusts Entra ID tokens directly, as shown above.
