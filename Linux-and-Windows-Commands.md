# Windows and Linux Command Line Cheatsheet

## Windows Command Line (CMD/PowerShell)

### File and Directory Operations
| Action | Command |
|--------|---------|
| List directory contents | `dir` |
| Change directory | `cd [directory]` |
| Make directory | `mkdir [directory]` |
| Remove directory | `rmdir [directory]` or `rd [directory]` |
| Remove directory (with contents) | `rmdir /s /q [directory]` |
| Create empty file | `type nul > [filename]` or `echo.> [filename]` |
| Copy file | `copy [source] [destination]` |
| Move file | `move [source] [destination]` |
| Delete file | `del [filename]` |
| Rename file/directory | `ren [oldname] [newname]` |
| Show file contents | `type [filename]` |
| Find text in file | `findstr "[text]" [filename]` |
| Compare files | `fc [file1] [file2]` |

### System Information
| Action | Command |
|--------|---------|
| Display system info | `systeminfo` |
| Display hostname | `hostname` |
| Display IP configuration | `ipconfig` |
| Detailed IP configuration | `ipconfig /all` |
| Show running processes | `tasklist` |
| Kill process | `taskkill /IM [process_name] /F` or `taskkill /PID [process_id] /F` |
| System services list | `net start` |
| Check disk | `chkdsk [drive]:` |
| Show date and time | `date` and `time` |

### Network Commands
| Action | Command |
|--------|---------|
| Ping a host | `ping [host]` |
| Trace route | `tracert [host]` |
| Show network connections | `netstat -an` |
| Network statistics | `netstat -e` |
| DNS lookup | `nslookup [domain]` |
| Download file | `curl -o [filename] [url]` (PowerShell) |

### User Management
| Action | Command |
|--------|---------|
| Current user | `whoami` |
| List users | `net user` |
| Add user | `net user [username] [password] /add` |
| Delete user | `net user [username] /delete` |
| Add to group | `net localgroup [group] [username] /add` |

### PowerShell Specific
| Action | Command |
|--------|---------|
| Get help | `Get-Help [command]` |
| Get commands | `Get-Command` |
| Get process | `Get-Process` |
| Get service | `Get-Service` |
| Set location | `Set-Location [path]` (alias: cd) |
| Get content | `Get-Content [file]` (alias: cat, type) |
| Get child items | `Get-ChildItem` (alias: dir, ls) |

### Batch Scripts
| Action | Command |
|--------|---------|
| Echo text | `echo [text]` |
| Comments | `REM [comment]` or `:: [comment]` |
| Pause execution | `pause` |
| Set variable | `set [var]=[value]` |
| Use variable | `%[var]%` |
| Conditional | `if [condition] (command)` |
| Loop | `for %i in ([set]) do [command]` |

## Linux Command Line (Bash)

### File and Directory Operations
| Action | Command |
|--------|---------|
| List directory contents | `ls` or `ls -la` (detailed) |
| Change directory | `cd [directory]` |
| Make directory | `mkdir [directory]` |
| Remove directory | `rmdir [directory]` |
| Remove directory (with contents) | `rm -rf [directory]` |
| Create empty file | `touch [filename]` |
| Copy file | `cp [source] [destination]` |
| Move file | `mv [source] [destination]` |
| Delete file | `rm [filename]` |
| Rename file/directory | `mv [oldname] [newname]` |
| Show file contents | `cat [filename]` |
| Show file contents (paged) | `less [filename]` or `more [filename]` |
| Find text in file | `grep "[text]" [filename]` |
| Compare files | `diff [file1] [file2]` |
| File permissions | `chmod [permissions] [filename]` |
| Change ownership | `chown [user]:[group] [filename]` |

### System Information
| Action | Command |
|--------|---------|
| Display system info | `uname -a` |
| Display hostname | `hostname` |
| Display IP configuration | `ifconfig` or `ip addr` |
| Show running processes | `ps aux` |
| Kill process | `kill [process_id]` or `killall [process_name]` |
| System services | `systemctl list-units --type=service` |
| Check disk space | `df -h` |
| Show memory usage | `free -h` |
| Show date and time | `date` |
| Show uptime | `uptime` |
| Show last logins | `last` |

### Network Commands
| Action | Command |
|--------|---------|
| Ping a host | `ping [host]` |
| Trace route | `traceroute [host]` |
| Show network connections | `netstat -tuln` |
| Network statistics | `netstat -s` |
| DNS lookup | `nslookup [domain]` or `dig [domain]` |
| Download file | `wget [url]` or `curl -O [url]` |

### User Management
| Action | Command |
|--------|---------|
| Current user | `whoami` |
| List users | `cat /etc/passwd` |
| Add user | `useradd [username]` |
| Set password | `passwd [username]` |
| Delete user | `userdel [username]` |
| Add to group | `usermod -aG [group] [username]` |
| Switch user | `su [username]` |
| Execute as superuser | `sudo [command]` |

### Package Management
| Action | Command (Debian/Ubuntu) | Command (Red Hat/Fedora) |
|--------|-------------------------|--------------------------|
| Update package list | `apt update` | `dnf check-update` |
| Install package | `apt install [package]` | `dnf install [package]` |
| Remove package | `apt remove [package]` | `dnf remove [package]` |
| Search package | `apt search [keyword]` | `dnf search [keyword]` |
| List installed packages | `dpkg -l` | `rpm -qa` |

### File Manipulation
| Action | Command |
|--------|---------|
| Find files | `find [path] -name "[pattern]"` |
| Count lines/words | `wc [filename]` |
| Sort content | `sort [filename]` |
| Unique lines | `uniq [filename]` |
| Head of file | `head [filename]` |
| Tail of file | `tail [filename]` |
| Follow file updates | `tail -f [filename]` |
| Create symbolic link | `ln -s [target] [linkname]` |
| Compress file (gzip) | `gzip [filename]` |
| Extract gzip file | `gunzip [filename.gz]` |
| Create tar archive | `tar -cvf [archive.tar] [files]` |
| Extract tar archive | `tar -xvf [archive.tar]` |

### Shell Scripting
| Action | Command |
|--------|---------|
| Echo text | `echo [text]` |
| Comments | `# [comment]` |
| Set variable | `[var]=[value]` |
| Use variable | `$[var]` |
| Conditional | `if [condition]; then [command]; fi` |
| Loop | `for i in [set]; do [command]; done` |
| Execute script | `bash [script.sh]` or `./[script.sh]` (with execute permissions) |

## Command Comparison: Windows vs. Linux

| Function | Windows (CMD/PowerShell) | Linux (Bash) |
|----------|--------------------------|--------------|
| List directory contents | `dir` | `ls` |
| Change directory | `cd [directory]` | `cd [directory]` |
| Clear screen | `cls` | `clear` |
| Copy file | `copy [source] [destination]` | `cp [source] [destination]` |
| Move/rename | `move [source] [destination]` | `mv [source] [destination]` |
| Delete file | `del [filename]` | `rm [filename]` |
| Create directory | `mkdir [directory]` | `mkdir [directory]` |
| Remove directory | `rmdir [directory]` | `rmdir [directory]` |
| Remove directory with contents | `rmdir /s /q [directory]` | `rm -rf [directory]` |
| Show file contents | `type [filename]` | `cat [filename]` |
| Find text in file | `findstr "[text]" [filename]` | `grep "[text]" [filename]` |
| Show running processes | `tasklist` | `ps aux` |
| Kill process | `taskkill /IM [name] /F` | `kill [PID]` or `killall [name]` |
| Show network config | `ipconfig` | `ifconfig` or `ip addr` |
| Ping host | `ping [host]` | `ping [host]` |
| File permissions | N/A (different system) | `chmod [permissions] [file]` |
| Execute as admin | `runas /user:Administrator [command]` | `sudo [command]` |
| Show system info | `systeminfo` | `uname -a` |
| Create empty file | `type nul > [filename]` | `touch [filename]` |
| Environment variables | `set` or `echo %[VARNAME]%` | `env` or `echo $[VARNAME]` |
| Path separator | `\` (backslash) | `/` (forward slash) |
| Command separator | `&` | `;` |
| Redirect output to file | `>` (overwrite) or `>>` (append) | `>` (overwrite) or `>>` (append) |
| Pipe output | `|` | `|` |
| Show help | `[command] /?` | `man [command]` |
| Show disk usage | `chkdsk` | `df -h` |
| Show file metadata | `dir [filename]` | `stat [filename]` |
| Search for files | `dir /s [pattern]` | `find [path] -name "[pattern]"` |
| Compare files | `fc [file1] [file2]` | `diff [file1] [file2]` |
| Download file | `curl -o [file] [url]` (PowerShell) | `wget [url]` or `curl -O [url]` |
| Shutdown system | `shutdown /s` | `shutdown -h now` |
| Restart system | `shutdown /r` | `reboot` or `shutdown -r now` |
| Schedule task | `schtasks` | `crontab` |
| View text file (paged) | `more [filename]` | `less [filename]` or `more [filename]` |
| Create symbolic link | `mklink [link] [target]` | `ln -s [target] [link]` |
| Show calendar | N/A | `cal` |
| Change file timestamp | N/A | `touch -t [timestamp] [file]` |

## Tips and Tricks

### Windows Tips
- Use Tab key for autocompletion
- Use arrow keys to navigate command history
- `doskey /history` shows command history
- PowerShell has more powerful scripting capabilities than CMD
- Use `Start-Transcript` in PowerShell to log your session
- Access special folders with environment variables like `%USERPROFILE%` or `%TEMP%`

### Linux Tips
- Use Tab key for autocompletion
- Up/down arrows for command history
- `history` shows command history
- Use `alias` to create shortcuts for commands
- Add `&` at the end of a command to run it in the background
- Use `Ctrl+R` for reverse history search
- Use `&&` to chain commands (second runs only if first succeeds)
- Redirect errors with `2>` (e.g., `command 2> errors.txt`)
- Use `sudo !!` to repeat the last command with sudo
- Use `~` as shorthand for your home directory
