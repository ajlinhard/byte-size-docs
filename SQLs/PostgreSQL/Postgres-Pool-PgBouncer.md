# Postgres Pools PgBouncer
Great choice! **PgBouncer** is the go-to connection pooler for PostgreSQL. Here's a complete setup guide:

---

## 1. Install PgBouncer

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install pgbouncer -y

# RHEL/CentOS
sudo yum install pgbouncer -y
```

---

## 2. Configure `pgbouncer.ini`

Edit `/etc/pgbouncer/pgbouncer.ini`:

```ini
[databases]
# Format: alias = host=... port=... dbname=...
mydb = host=127.0.0.1 port=5432 dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432

auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

; Pool mode options: session | transaction | statement
pool_mode = transaction

; Max connections to PostgreSQL backend
max_client_conn = 100
default_pool_size = 20

logfile = /var/log/pgbouncer/pgbouncer.log
pidfile = /var/run/pgbouncer/pgbouncer.pid
```

**Pool mode guide:**
| Mode | Description | Best for |
|---|---|---|
| `session` | One server conn per client session | Legacy apps |
| `transaction` | Conn released after each transaction ✅ | Most apps |
| `statement` | Conn released after each statement | Stateless only |

---

## 3. Set Up `userlist.txt`

PgBouncer needs a list of users and their **MD5-hashed** passwords:

```bash
# Generate MD5 hash (format: md5 + md5(password + username))
echo -n "md5$(echo -n 'mypasswordmyuser' | md5sum | cut -d' ' -f1)"
```

Then add to `/etc/pgbouncer/userlist.txt`:

```
"myuser" "md5<hash_from_above>"
```

---

## 4. Start & Enable PgBouncer

```bash
sudo systemctl start pgbouncer
sudo systemctl enable pgbouncer
sudo systemctl status pgbouncer
```

---

## 5. Connect Through PgBouncer

Just point your app to port **6432** instead of 5432:

```bash
psql -h 127.0.0.1 -p 6432 -U myuser -d mydb
```

---

## 6. Monitor PgBouncer

Connect to the admin console:

```bash
psql -h 127.0.0.1 -p 6432 -U pgbouncer pgbouncer
```

Useful commands inside:
```sql
SHOW POOLS;      -- connection pool stats
SHOW CLIENTS;    -- connected clients
SHOW SERVERS;    -- backend connections
SHOW STATS;      -- throughput metrics
```

---

## Common Gotchas

- **`SET` statements / prepared statements** don't work well in `transaction` mode — switch to `session` mode if your app uses them heavily.
- **`pg_hba.conf`** on your PostgreSQL server should allow connections from PgBouncer's IP.
- If using **SSL**, add `server_tls_sslmode = require` to `pgbouncer.ini`.

---

Want help with anything specific — like tuning pool sizes, setting up for a cloud DB (RDS, Supabase, etc.), or configuring with Docker?
