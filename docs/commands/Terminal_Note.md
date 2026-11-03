# Terminal note — read before running any commands file

The commands in this directory are written for a **Linux shell (bash)**. That's the shell CI,
the VPS and the Docker containers use.

- **Linux:** run them as written.
- **macOS:** most run as written in Terminal (zsh). Where a command behaves differently on
  macOS (for example `sed -i`, `sha256sum`, `readlink -f`), look up the macOS equivalent.
- **Windows** (PowerShell, Command Prompt or Windows Terminal): look up the equivalent of any
  command that isn't Windows-native. A few steps already give a PowerShell form, labelled
  `PowerShell:`. Common ones:

  | bash | PowerShell | Command Prompt (cmd) |
  |---|---|---|
  | `cp a b` | `Copy-Item a b` | `copy a b` |
  | `unzip -o file.zip` | `Expand-Archive -Force file.zip .` | `tar -xf file.zip` |
  | `grep text file` | `Select-String text file` | `findstr text file` |
  | `export NAME=value` | `$env:NAME = "value"` | `set NAME=value` |
  | `\` at a line end (continue) | `` ` `` (backtick) | `^` |

  Alternatively, run the commands unchanged in **WSL** or **Git Bash**.

**These run the same everywhere:** `docker …`, `docker compose …`, `npm …` and `git …`.
Commands run *inside* a container (`docker compose … exec web …`) are always Linux commands,
whatever your own machine runs. Commands run on the VPS over SSH are Linux commands too.
