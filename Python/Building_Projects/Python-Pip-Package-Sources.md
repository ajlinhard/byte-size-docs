# Python Pip Package
When working with pip by default it is pulling packages from the public PyPI package repository. This is a configurable setting in your local pip, as well as other services like uv/poetry. There is tiers at which you can apply these settings in a hierarchy, so it can be project specific, user level, or global on your computer.

## Where is current Package Repository Info
`~` expands to:

- Linux: `/home/yourname`
- macOS: `/Users/yourname`
- Windows: `C:\Users\yourname` (and the file is `pip.ini`, under `%APPDATA%\pip\`)

Neither the folder nor the file exists until you create it — that's why the instructions say to add it.

**Ask pip directly.** This prints every location pip will look at, in precedence order, and marks which ones exist:

```bash
python3.14 -m pip config debug
```

You'll see up to four tiers: global (`/etc/pip.conf`), user (`~/.config/pip/pip.conf` and the legacy `~/.pip/pip.conf`), and site — the site one being `<venv>/pip.conf`, which *is* tied to a specific environment.

### Virtual Environments
**If you want the config to apply only to a 3.14 venv**, put it in the venv root instead:

```bash
python3.14 -m venv myenv
echo "[global]" > myenv/pip.conf
echo "index-url = https://..." >> myenv/pip.conf
```

That beats the user-level file when the venv is active, which is handy if only one project needs Artifactory.

Separately — if what you're actually after is where pip's *code* lives in 3.14, that's `.../python3.14/site-packages/pip/`, findable via `python3.14 -m pip -V`. But nothing you configure goes there.

---
## Installing a User Level Artifactory
That instruction comes from Artifactory's "Set Me Up" dialog, which hands you a config block to paste. Here's the mechanics.

**Create the file**

```bash
mkdir -p ~/.pip
touch ~/.pip/pip.conf
```

(`~/.pip/pip.conf` is the legacy location but pip still honors it. The modern path is `~/.config/pip/pip.conf`; on Windows it's `%APPDATA%\pip\pip.ini`.)

**Add the index URL**

```ini
[global]
index-url = https://<your-instance>.jfrog.io/artifactory/api/pypi/<repo-name>/simple
```

`<repo-name>` is usually a virtual repo like `pypi` or `pypi-remote` that proxies PyPI and overlays your internal packages. The `/simple` suffix matters — that's the PEP 503 index endpoint.

**Credentials**

Artifactory's Set Me Up often gives you an inline-credential URL:

```ini
index-url = https://<user>:<token>@<instance>.jfrog.io/artifactory/api/pypi/<repo>/simple
```

That works, but it puts a token in a plaintext file. Two better options:

*Netrc* — keep the URL clean and put credentials in `~/.netrc`, which pip reads automatically:

```
machine <instance>.jfrog.io
login <your-email-or-username>
password <identity-token>
```

Then `chmod 600 ~/.netrc`.

*Environment variable* — `PIP_INDEX_URL` overrides the config file, useful for CI where you inject a secret at runtime.

Either way, use an identity token or API key rather than your account password.

**Verify**

```bash
pip config debug          # confirms pip sees the file and the value
pip install -v requests   # first lines show "Looking in indexes: ..."
```

If `pip config debug` doesn't list your file, you're likely on a pip version or platform expecting the other path — just create it at `~/.config/pip/pip.conf` instead.

One caution given the earlier thread: use `index-url`, not `extra-index-url`. With `extra-index-url` pip queries both Artifactory and public PyPI and takes the highest version, which reopens the dependency-confusion hole that routing through Artifactory was meant to close.
