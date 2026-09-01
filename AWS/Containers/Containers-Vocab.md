# Containers Vocab

### **Stateless** 
Each request is handled independently, with nothing remembered from the last one. No user session, no in-memory cache of "who's logged in," no partial workflow data sitting in the pod's memory. If a request needs context (who the user is, what step they're on), that context has to arrive *with* the request — e.g. in a cookie, a token, or a query param — rather than being looked up from something the server remembers.

### **No PVC** 
PVC stands for Persistent Volume Claim, a Kubernetes concept. It's how a pod requests a chunk of durable storage (backed by disk, cloud block storage, etc.) that survives independently of the pod's own lifecycle. "No PVC" means the front end isn't mounting any of that — it has no durable disk it can write to and read back later.

### **No local persistent storage**
even setting Kubernetes aside, the pod isn't relying on its own local filesystem to remember anything either. Whatever gets written to a container's local disk disappears the moment that container is killed or rescheduled anyway — this just makes explicit that the app isn't even trying to use it as a stopgap.

**What it adds up to:** every front-end pod is fully disposable and interchangeable. Kubernetes can kill one, spin up a replacement on a different node, scale from 2 replicas to 20, or restart the whole deployment — and nothing breaks, because no pod is holding onto anything unique. Any real state (the logged-in user, their session, application data) has to live somewhere else: the browser (cookies, `sessionStorage`, `localStorage`) or a backend/database th
