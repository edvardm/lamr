# LAMR

Ain't makefile replacement, but it might help you managing those.

[![asciicast](demo.gif)](demo.gif)

## Overview

LAMR is a simple tool to manage makefiles in such a way that generic rules
are separated from project specific ones, and provides means to easily sync
shared makefiles reducing duplication.

It should be especially useful if you have several projects using same
languages/technologies, and want to provide automation for standard tasks like
formatting, linting, deploying without duplicating lots of code.

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

## Makefile repositories

In order to have those shared makefiles, you need to have a repository for those.
There's only these few requirements you need to have so that LAMR is able to
use that repository:

- Project root has subdirectory `makefiles`
- Makefiles should have `.mk` extension, named according to technology/feature

As an example, see https://github.com/edvardm/makefiles

## Configuration

You can configure repository to use for Makefiles in an rc file. These files will be tried in order using the first found:

`.lamrrc` in current directory, `$XDG_CONFIG_HOME/lamrrc` and `$HOME/.lamrrc`.

For now, the only supported key is `lamr.repository`. Eg.

```
[lamr]
repository = edvardm/makefiles
# shortcut for git@github.com:edvardm/makefiles'
```
## Development

Run `make setup test`, ensure all tests are green, and you're good to go.

## FAQ

- **Do I need to change my existing Makefiles?** No, using `include` in your Makefile helps to adopt LAMR by separating more generic rules from project-specific
- **Can I put other shared things there in addition to makefiles?** LAMR would ignore those for now, but it's pretty much unaware of any make-specific things, so maybe in near future
- **But I don't want to blindly push things to shared repo** That's not a question. You can use `git add --interactive` though in a repository where you want pull changes to to cherry-pick only those changes you want. See next question too
- **Can I make PRs to shared repositories instead of just pushing stuff there?** Not yet through LAMR, but that might be useful feature later on
- **Do I need remote repository for shared files?** No, you can give `--repo` any URL to a repository you have at least read access to, including local repositories
