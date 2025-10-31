# Postgres Local Connection

## PostgreSQL in 60 Seconds

## Copy-Paste This:

```bash
# 1. Start PostgreSQL
docker run --name pg -e POSTGRES_PASSWORD=test -p 5432:5432 -d postgres:16

# 2. Wait 5 seconds, then connect
docker exec -it pg psql -U postgres

# 3. Inside psql, test it:
SELECT * FROM test;
```

## Use in Your Code:

**Connection String:**
```
postgresql://postgres:test@localhost:5432/postgres
```

**Python:**
```python
import psycopg2
conn = psycopg2.connect("postgresql://postgres:test@localhost:5432/postgres")
```

**Node.js:**
```javascript
const { Client } = require('pg');
const client = new Client({connectionString: 'postgresql://postgres:test@localhost:5432/postgres'});
```

## Done Testing?

```bash
docker rm -f pg
```

**That's it.**

### Psycopg2
```python
import psycopg2
conn = psycopg2.connect("postgresql://postgres:test@localhost:5432/postgres")
```

### pg8000
```python
import pg8000
conn = pg8000.connect(host='localhost', port=5432, database='postgres', user='postgres', password='test')
```

### PgAdmin
You can also connect to this local database on your pgAdmin IDE. 


**Other version examples:**
```bash
postgres:16      # PostgreSQL 16 (latest 16.x)
postgres:15      # PostgreSQL 15
postgres:latest  # Most recent version (not recommended for production)
postgres:16.1    # Specific minor version
```

---

## What Happens When You Run This?

```bash
docker run --name pg -e POSTGRES_PASSWORD=test -p 5432:5432 -d postgres:16
```

**Step-by-step:**

1. **Docker checks locally**: "Do I have `postgres:16`?"
   - If NO → Download from Docker Hub (~100-150 MB)
   - If YES → Use cached image

2. **Creates a container** named "pg" from the `postgres:16` image

3. **Sets environment variable**: `POSTGRES_PASSWORD=test`

4. **Maps ports**: Your computer's port 5432 → Container's port 5432

5. **Starts in background** (detached mode)

6. **PostgreSQL initializes**:
   - Creates data directory
   - Initializes database cluster
   - Creates default `postgres` database
   - Sets password to `test`
   - Starts listening on port 5432 (inside container)

7. **Returns container ID** (long hash like `a3f2b8c9d...`)

---

## Visual Representation

```
YOUR COMPUTER (Host)              DOCKER CONTAINER
┌─────────────────────┐          ┌──────────────────────┐
│                     │          │  Name: pg            │
│  localhost:5432 ────┼─────────►│  Port 5432           │
│                     │          │                      │
│  Your code connects │  Maps to │  PostgreSQL 16       │
│  here               │          │  Password: test      │
│                     │          │  Running in bg       │
└─────────────────────┘          └──────────────────────┘
```

---

## Equivalent Longer Form

This short command:
```bash
docker run --name pg -e POSTGRES_PASSWORD=test -p 5432:5432 -d postgres:16
```

Is equivalent to:
```bash
docker run \
  --name pg \                          # Name the container
  --env POSTGRES_PASSWORD=test \       # Set password
  --publish 5432:5432 \                # Map ports
  --detach \                           # Run in background
  postgres:16                          # Image to use
```

---

## Common Variations

### Add persistent storage (data survives container deletion):
```bash
docker run --name pg \
  -e POSTGRES_PASSWORD=test \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \  # NEW: volume mount
  -d postgres:16
```

### Use custom database name and user:
```bash
docker run --name pg \
  -e POSTGRES_USER=myuser \             # Custom user
  -e POSTGRES_PASSWORD=test \
  -e POSTGRES_DB=mydb \                 # Custom database name
  -p 5432:5432 \
  -d postgres:16
```

### Different port to avoid conflicts:
```bash
docker run --name pg \
  -e POSTGRES_PASSWORD=test \
  -p 5433:5432 \                        # Host uses 5433
  -d postgres:16

# Connect with: postgresql://postgres:test@localhost:5433/postgres
```

---

## Verification

**Check if it's running:**
```bash
docker ps

# Output shows:
# CONTAINER ID   IMAGE         NAMES   PORTS
# a3f2b8c9d...   postgres:16   pg      0.0.0.0:5432->5432/tcp
```

**Check logs:**
```bash
docker logs pg

# Should see:
# PostgreSQL init process complete; ready for start up.
# database system is ready to accept connections
```

**Connect and test:**
```bash
docker exec -it pg psql -U postgres
# You're now inside PostgreSQL!
```

That's the complete breakdown! The key takeaway: Docker automatically downloads the official PostgreSQL image from Docker Hub and runs it with your specified configuration.
