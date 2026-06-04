# Conda Ananconda Env Variables
Here's how to list and change variables in your Anaconda environment:

## Listing Environment Variables

**List all conda environments:**
```bash
conda env list
# or
conda info --envs
```

**List packages/dependencies in the active environment:**
```bash
conda list
```

**List packages in a specific environment:**
```bash
conda list -n myenv
```

**List environment variables (env vars) set in the environment:**
```bash
conda env config vars list
# or for a specific env:
conda env config vars list -n myenv
```

---

## Changing/Setting Environment Variables

**Set an environment variable in the active environment:**
```bash
conda env config vars set MY_VAR=value
```

**Set a variable in a specific environment:**
```bash
conda env config vars set MY_VAR=value -n myenv
```

**Unset/remove an environment variable:**
```bash
conda env config vars unset MY_VAR
# or for a specific env:
conda env config vars unset MY_VAR -n myenv
```

> After setting or unsetting variables, **reactivate the environment** for changes to take effect:
> ```bash
> conda activate myenv
> ```

---

## Switching Between Environments

**Activate a different environment:**
```bash
conda activate myenv
```

**Deactivate the current environment:**
```bash
conda deactivate
```

---

## Quick Tips

- `conda env config vars` changes are **persistent** — they survive terminal restarts.
- For **temporary** changes in the current session only, just use the standard shell command: `export MY_VAR=value` (Mac/Linux) or `set MY_VAR=value` (Windows CMD).
- You can also define env vars in an `environment.yml` file under the `variables:` key for reproducibility.
