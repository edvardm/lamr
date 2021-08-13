# LAMR

Ain't makefile replacement, but it might help you managing those.

[![asciicast](demo.gif)](demo.gif)

## Overview

LAMR is a simple tool to manage makefiles in such a way that generic rules are separated from project specific ones, and provides means to easily sync shared makefiles reducing duplication.

It should be especially useful if you have several projects using same languages/technologies, and want to
provide automation for standard tasks like formatting, linting, deploying without duplicating lots of code.

## Details

Projects using LAMR would basically have project-specific `Makefile` at project root, and one or more generic, shared makefiles hosted elsewhere in a separate repository. You could do this without using any tool, but it would be bothersome to manually keep those in sync with local changes and other projects. 

This is where LAMR comes in. It allows for quick installation of your favorite Makefile rules, and helps in syncing changes to shared rules.

Design philosophy is to avoid reinventing the wheel, meaning that Makefiles are still
just plain, old Makefiles, Git is used to manage shared files etc.

There's a sample repository with shared makefiles at `https://github.com/edvardm/makefiles`, but you probably want to create your own and point `lamr` to that instead.

## Requirements

- Bash-compatible shell in a POSIX-compliant environment. At least Linux and MacOS should be fine
- Python >= 3.7 (3.x should be fine, but haven't tested)
## Installation

In your project root directory, run

```bash
curl -ssL "https://raw.githubusercontent.com/edvardm/lamr/master/bootstrap.sh" -o lamr.sh
chmod +x lamr.sh && ./lamr.sh
```

If you have several developers in your project, you might want to add that script to version control, so that
getting LAMR is as easy as running `./lamr.sh` at project root.
## Usage

`lamr <cmd>` where `cmd` is one of the following:

- `install` will add stub Makefile to your project, including shared `.mk` files

- `pull` will update local, shared makefiles by replacing any files that have more recent version in shared makefile repository

- `push` will push any modified `.mk` files to remote repository.


See `lamr --help` for more info.

## Development

Run `make setup test`, ensure all tests are green, and you're good to go.

## Future ideas

- Instead of directly pushing local changes to shared repository, make it possible to use `lamr` to create PR instead
- Better error handling
