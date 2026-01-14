# SQL Alchemy - Post Sesson Access
SQL Alchemy by default likes to operate within the session you have running for your database. There can be issues if you operate on the SQL Alchemy objects outside of a sessions. However there are cases where you may want to do so.

## Patterns for Operations
No, not directly. Once you exit the session context, the object becomes **detached** from the session. While you can still read its attributes, any modifications won't be tracked or persisted automatically.

Here are your options:

## 1. **Merge the object back** (recommended for your pattern)

```python
# Retrieve
with db_handler.get_session() as session:
    claim = session.query(Claims).filter(Claims.claim_id == int(claim_id)).first()
    return claim

# Later, modify and update
claim.status = "approved"  # Modify the detached object

with db_handler.get_session() as session:
    claim = session.merge(claim)  # Merge it back
    session.commit()
```

## 2. **Re-query and update in a new session**

```python
# Later update
with db_handler.get_session() as session:
    claim = session.query(Claims).filter(Claims.claim_id == int(claim_id)).first()
    claim.status = "approved"
    session.commit()
```

## 3. **Keep the session open longer** (not recommended with context managers)

```python
# Don't use 'with' if you need the session to stay open
session = db_handler.get_session()
claim = session.query(Claims).filter(Claims.claim_id == int(claim_id)).first()
# ... do work ...
claim.status = "approved"
session.commit()
session.close()  # Must manually close
```

## Common pitfall to watch for:

```python
# This WON'T work - lazy loading will fail
with db_handler.get_session() as session:
    claim = session.query(Claims).filter(Claims.claim_id == int(claim_id)).first()

# Outside session - this will raise an error if relationships weren't loaded
claim.related_items  # DetachedInstanceError!
```

**Best practice**: Use `merge()` or re-query in a fresh session when you need to update detached objects.

## Possible Errors

```python
# Fetch claim
claim = None
with DB.get_session() as session:
    claim = session.query(Claims).filter(Claims.claim_id == int(claim_id)).first()
    if not claim:
        return build_error_response(404, f'Claim {claim_id} not found', claim_id=claim_id)
    if not claim.veteran_id:
        return build_error_response(500, f'Claim {claim_id} has no veteran_id', claim_id=claim_id)
    pid = claim.veteran_id

print(f"[init] claim_id={claim_id}, pid={pid}")

if claim.claim_id > 0
  return True
```

```text
sqlalchemy.orm.exc.DetachedInstanceError: Instance <Claims at 0x7fbdcd3e2e10> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: https://sqlalche.me/e/20/bhk3)
```
The error occurs because you're accessing `claim.claim_id` **outside** the session context, and SQLAlchemy is trying to refresh the attribute but can't find an active session.

## Quick Fix: Access all attributes inside the session

```python
# Fetch claim
claim = None
pid = None
with DB.get_session() as session:
    claim = session.query(Claims).filter(Claims.claim_id == int(claim_id)).first()
    if not claim:
        return build_error_response(404, f'Claim {claim_id} not found', claim_id=claim_id)
    if not claim.veteran_id:
        return build_error_response(500, f'Claim {claim_id} has no veteran_id', claim_id=claim_id)
    
    # Access attributes INSIDE the session before it closes
    pid = claim.veteran_id
    stored_claim_id = claim.claim_id  # Access it here

print(f"[init] claim_id={stored_claim_id}, pid={pid}")

if stored_claim_id > 0:
    # ... rest of code
```

## Better Fix: Use `expire_on_commit=False`

```python
with DB.get_session() as session:
    session.expire_on_commit = False  # Prevent expiring objects on commit
    claim = session.query(Claims).filter(Claims.claim_id == int(claim_id)).first()
    if not claim:
        return build_error_response(404, f'Claim {claim_id} not found', claim_id=claim_id)
    if not claim.veteran_id:
        return build_error_response(500, f'Claim {claim_id} has no veteran_id', claim_id=claim_id)
    pid = claim.veteran_id

# Now you can access claim.claim_id outside the session
print(f"[init] claim_id={claim.claim_id}, pid={pid}")

if claim.claim_id > 0:
    # This works now
```

## Alternative: Convert to a dict or DTO

```python
with DB.get_session() as session:
    claim = session.query(Claims).filter(Claims.claim_id == int(claim_id)).first()
    if not claim:
        return build_error_response(404, f'Claim {claim_id} not found', claim_id=claim_id)
    if not claim.veteran_id:
        return build_error_response(500, f'Claim {claim_id} has no veteran_id', claim_id=claim_id)
    
    # Create a simple dict with the data you need
    claim_data = {
        'claim_id': claim.claim_id,
        'veteran_id': claim.veteran_id,
        'status': claim.status,
        # ... other fields you need
    }

print(f"[init] claim_id={claim_data['claim_id']}, pid={claim_data['veteran_id']}")
```

**Why this happens**: When a session closes, SQLAlchemy marks objects as "expired" by default. When you try to access an attribute, it attempts to refresh from the database, but there's no session available.

The `expire_on_commit=False` solution is usually the cleanest if you need to pass the object around but won't be modifying it.
