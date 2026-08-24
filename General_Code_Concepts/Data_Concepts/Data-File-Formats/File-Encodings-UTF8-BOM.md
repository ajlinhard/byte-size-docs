# File Encodings UTF-8 BOM
When working with UTF or even more specifically UTF-8 there are a couple little "gotchas" which can occur mainly when going between system OS.
Example: The newline characters in files: \r\n vs \r or \n

There are even some more specific items like file prefix and suffixes
## UTF-8 BOM Error:
```
An error occurred (InvalidRequestContentException) when calling the Invoke operation: Could not parse request body into json: Could not parse payload into json: Invalid UTF-8 start byte 0xaf
 at [Source: REDACTED (StreamReadFeature.INCLUDE_SOURCE_IN_LOCATION disabled); line: 1, column: 3]
```
That error is a byte-order mark (BOM) at the front of `payload.json`, not a problem with your command. Jackson chokes on the BOM bytes before it ever sees the `{` — hence "line: 1, column: 3."

**Confirm it:**

```powershell
Format-Hex .\payload.json | Select-Object -First 1
```

If the first bytes are `EF BB BF` you have a UTF-8 BOM. If they're `FF FE` the file is UTF-16LE — that's what Windows PowerShell 5.1 produces when you create a file with `>` or `Out-File` with no `-Encoding`.

**Fix — rewrite the file as UTF-8 without BOM:**

```powershell
# PowerShell 7+
Set-Content -Path payload.json -Value '{"name":"world"}' -Encoding utf8NoBOM
```

```powershell
# Windows PowerShell 5.1 (Set-Content -Encoding utf8 still writes a BOM)
[System.IO.File]::WriteAllText(
    (Join-Path $PWD 'payload.json'),
    '{"name":"world"}',
    (New-Object System.Text.UTF8Encoding($false))
)
```

Then rerun your original command unchanged — it's correct as written, including the `--cli-binary-format raw-in-base64-out` flag that v2 needs.

**If you'd rather skip the file entirely**, PowerShell's quote handling makes inline JSON painful, so escape the inner quotes:

```powershell
aws lambda invoke `
    --profile va-vdi `
    --function-name entra-basic-basic-dev-hello `
    --payload '{\"name\":\"world\"}' `
    --cli-binary-format raw-in-base64-out `
    out.json
```

One thing worth watching: if you're editing `payload.json` in VS Code, check the encoding indicator in the status bar and set it to "UTF-8" rather than "UTF-8 with BOM," or the BOM will come back on the next save.

## Powershell Version Diffs:
That enum list confirms you're on Windows PowerShell 5.1 — `utf8NoBOM` only exists in PowerShell 7+. Use the .NET call instead:

```powershell
[System.IO.File]::WriteAllText(
    (Join-Path $PWD 'payload.json'),
    '{"hello":"world"}',
    (New-Object System.Text.UTF8Encoding($false))
)
```

The `$false` is the important bit — it's the `encoderShouldEmitUTF8Identifier` parameter, so you get UTF-8 with no BOM. Note the `Join-Path $PWD` wrapper: `WriteAllText` uses .NET's working directory, which in PowerShell is often not the directory your prompt shows, so a bare `'payload.json'` can silently write somewhere unexpected.

Verify before rerunning:

```powershell
Format-Hex .\payload.json | Select-Object -First 1
```

You want the first byte to be `7B` (that's `{`), with no `EF BB BF` or `FF FE` in front of it.

Worth noting for the future: in 5.1, every built-in redirection and cmdlet will fight you on this. `>`, `Out-File`, and `Set-Content -Encoding UTF8` all emit a BOM (and bare `>` defaults to UTF-16LE). `-Encoding Ascii` happens to work for plain-ASCII JSON since it writes no BOM, but it'll mangle any non-ASCII characters in your payload, so the .NET call is the safer habit.
