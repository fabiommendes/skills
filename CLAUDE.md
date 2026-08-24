This project is both a Python CLI tool for managing AI coding agents skills and
a collection of pre-build skills for some different tasks.


## CLI tool

The CLI tool uses typer and rich. It manages a database of skills stored under
~/.local/share/skills/*. It can be used to add, remove, list, and search skills.

The CLI can copy skills to and from a local directory. The tool should follow
good coding practices with tests, type hints, and documentation. All new feature
should include unit tests and should be validated against the test suite and
the static analysis tools before accepting changes.


## Skills

Never add new skills unless explicitly asked. Ignore this directory for the
most part.
