# Installation

## Prerequisites

- **Python 3.11 or newer.** GitIntel declares `requires-python = ">=3.11"` and is tested on
  3.11 through 3.14 in CI.
- **A C toolchain — only if no `pygit2` wheel exists for your platform.** On mainstream
  Linux/macOS/Windows targets `pygit2` ships binary wheels and no compiler is needed. On other
  platforms, `pip` builds it from source and requires libgit2's build dependencies.
- **Git itself is not required.** Repository access goes through libgit2 via `pygit2`.

Check your interpreter first:

```bash
python3 --version
```

## Install the CLI

=== "pipx (recommended)"

    [pipx](https://pipx.pypa.io/) installs the CLI into its own isolated environment and puts
    `gitintel` on your `PATH`:

    ```bash
    pipx install gitintel
    ```

    Upgrade later with:

    ```bash
    pipx upgrade gitintel
    ```

=== "pip"

    ```bash
    python -m pip install gitintel
    ```

    Prefer a virtual environment so GitIntel's dependencies do not mix with your project's:

    ```bash
    python -m venv .venv
    source .venv/bin/activate      # Windows: .venv\Scripts\activate
    python -m pip install gitintel
    ```

=== "uv"

    ```bash
    uv tool install gitintel
    ```

    Or run it once without installing anything permanently:

    ```bash
    uvx gitintel analyze .
    ```

=== "From source"

    ```bash
    git clone https://github.com/ThePhoenix77/GitIntel.git
    cd GitIntel
    python -m pip install -e .
    ```

    For a full development environment (tests, linter, build tooling) see
    [Development setup](../development/setup.md).

## Verify the installation

```bash
gitintel --version
```

```text
0.1.0
```

Both of the following are equivalent and print the same value:

```bash
gitintel version
gitit --version
```

`gitit` is an alias entry point registered by the package; every command and option documented
here works identically under either name.

If the shell reports `command not found`, see
[Troubleshooting → `gitintel: command not found`](../troubleshooting/index.md#gitintel-command-not-found).

## Run without installing

GitIntel is also runnable as a module, which is convenient inside a checkout or a CI job that
installed it into a virtual environment:

```bash
python -m gitintel analyze .
```

## Shell completion

Typer provides completion for Bash, Zsh, Fish, and PowerShell:

```bash
gitintel --install-completion
```

Restart your shell afterwards. To inspect the generated script instead of installing it, use
`gitintel --show-completion`.

## Uninstall

=== "pipx"

    ```bash
    pipx uninstall gitintel
    ```

=== "pip"

    ```bash
    python -m pip uninstall gitintel
    ```

GitIntel keeps one piece of state outside the installed package: the clone cache for remote
repositories. Remove it if you want a completely clean system:

```bash
rm -rf ~/.cache/gitintel        # or "$XDG_CACHE_HOME/gitintel"
```

See [Repository sources and cache](../concepts/repository-sources.md) for details.
