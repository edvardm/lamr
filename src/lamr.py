#!/usr/bin/env python3

import argparse
import functools
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

RESOURCE_DIR = Path("makefiles")
DEFAULT_INCLUDE_PATH = Path("include")

TIMEOUT = int(os.getenv("TIMEOUT", "30"))
CACHE_DIR = Path(os.environ["HOME"]) / ".cache" / "lamr"

__VERSION__ = "2021-04.1001"


class EmptyResourceDir(Exception):
    pass


def main():
    args = _parse_args()

    _dispatch(args.cmd)(args)


def install(args):
    info = _printer(args)
    notice = compose(info, _fmt_notice)

    info(f"Installing makefiles from {_repo_url(args)}..")

    os.makedirs(args.include, exist_ok=True)
    included_files = []

    for repo_makefile in _list_makefiles(args):
        dst = args.include / repo_makefile.name

        if dst.exists() and not args.force:
            notice(f"{dst} already present, refusing to override")
        else:
            _local_sync(repo_makefile, dst)
            included_files.append(dst)

    _write_main_makefile(included_files)

    if included_files:
        info(
            f"""
Added {_fmt_notice("Makefile")} to project root and {_fmt_success(len(included_files))} shared makefile(s).

Feel free to add any custom rules to root Makefile, and don't forget to check
out existing rules in included files under {args.include} directory.
    """
        )


def pull(args):
    """Pull and update all shared makefiles from upstream"""

    if not args.include.is_dir():
        sys.exit(
            f"No files found in directory '{args.include}'. Run install first or specify '--include' to point to correct directory"
        )

    info = _printer(args)
    debug = _debug(args)
    notice = compose(info, _fmt_notice)
    updated = 0

    debug(f"Using cache {CACHE_DIR}")

    info(f"Refreshing cached copy of {_repo_url(args)}...")
    _update_local_copy(args)

    for upstream_makefile in _list_makefiles(args):
        project_makefile = args.include / upstream_makefile.name

        if not project_makefile.exists():
            debug("ignoring {project_makefile} as it is not included")
            continue

        delta_mtime = (
            project_makefile.stat().st_mtime - upstream_makefile.stat().st_mtime
        )
        if args.force or delta_mtime < 0:
            info(f"updating {project_makefile}")
            _local_sync(upstream_makefile, project_makefile)
            updated += 1
        elif delta_mtime == 0:
            notice(f"skipping unchanged {project_makefile}")
        else:
            notice(f"{project_makefile} is more recent, skipping")

    info(f"{updated} file(s) updated")


def list(args):  # pylint: disable=redefined-builtin
    info = _printer(args)
    _debug(args)

    info(f"Listing available makefiles in {args.repo}... ")
    try:
        for fpath in _list_makefiles(args):
            print(fpath.name)
    except EmptyResourceDir:
        print(_fmt_error(f"No shared makefiles in {args.repo}"))
        sys.exit(1)


def push(args):
    """Push local changes to shared files to upstream"""

    # TODO: add --pr option, maybe using `gh` tool?
    if not args.include.is_dir():
        sys.exit(
            _fmt_error(
                f"No files found in {args.include}. Run install first or specify "
                "'--include' to point to correct directory"
            )
        )

    info = _printer(args)
    debug = _debug(args)

    debug(f"Using cache {CACHE_DIR}")
    info(f"Refreshing cached copy of {_repo_url(args)}...")
    cached_repo = _cache_remote_repo(args)

    modified = []
    added = []

    try:
        for project_makefile in Path(args.include).glob("*.mk"):
            upstream_makefile = cached_repo / RESOURCE_DIR / project_makefile.name
            is_new_file = not upstream_makefile.exists()

            local_copy_newer = is_new_file or _mtime(project_makefile) > _mtime(
                upstream_makefile
            )
            debug(
                f"{project_makefile} is newer than {upstream_makefile}: {local_copy_newer}"
            )

            if local_copy_newer:
                modified.append(project_makefile)
                info(f"copy {project_makefile} to {upstream_makefile}")
                _local_sync(project_makefile, upstream_makefile)

                if is_new_file:
                    added.append(project_makefile.name)
            else:
                info(_fmt_notice(f"no changes to {project_makefile}, skipping"))

        if added:
            info(
                _fmt_notice(
                    f"Adding {len(added)} new files to shared repository {args.repo}"
                )
            )
            new_files = " ".join(str(RESOURCE_DIR / fname) for fname in added)
            _sys_exec(args, f"cd {cached_repo} && git add {new_files}")

        updates = len(added) + len(modified)
        if updates > 0:
            debug(f"Adding {updates} updated/new files to git")
            _sys_exec(
                args,
                f"cd {cached_repo} && git add {RESOURCE_DIR} && git commit -v && git push",
                interactive=True,
            )

    except Exception:  ## pylint: disable=broad-except
        # undo local changes in cached repository
        _sys_exec(
            args,
            f"cd {cached_repo} && (git reset {RESOURCE_DIR} && git checkout {RESOURCE_DIR} && git clean -df)",
        )
        raise


def version(_):
    print(f"version {__VERSION__}")


def _mtime(fpath):
    return fpath.stat().st_mtime


def _local_sync(src, dst):
    # copy file including local access and mtime
    shutil.copyfile(src, dst)
    shutil.copystat(src, dst)


def _dispatch(fun):
    return getattr(sys.modules[__name__], fun)


def _parse_args():
    def multi_value_str(string) -> List[str]:
        if not string:
            return []
        return [s.strip() for s in string.split(",")]

    parser = argparse.ArgumentParser(
        description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("cmd", choices=("install", "list", "pull", "push", "version"))
    parser.add_argument("--force", "-f", action="store_true", help="Force any actions")
    parser.add_argument(
        "--repo",
        "-r",
        type=str,
        required=True,
        help="Repository to get makefiles from",
    )
    parser.add_argument(
        "--include",
        type=Path,
        default=DEFAULT_INCLUDE_PATH,
        help="Directory to store shared makefiles to",
    )
    parser.add_argument(
        "--branch",
        "-b",
        type=str,
        default="master",
        help="Branch to use for makefile repository",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Produce more output"
    )
    parser.add_argument(
        "--only",
        "-o",
        type=multi_value_str,
        help="Include only given shared files, separate multiple entries by comma",
    )

    parser.add_argument(
        "--debug", "-d", action="store_true", help="Produce debug-level output"
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Be rather quiet")

    return parser.parse_args()


def _write_main_makefile(includes):
    with open("Makefile", "w") as fh:
        for fname in sorted(includes):
            fh.write(f"include {fname}\n")

        fh.write(
            """
SRC ?= src
        """
        )


def _list_makefiles(args):

    cached_repo = _cache_remote_repo(args)
    resource_path = Path(cached_repo) / RESOURCE_DIR

    files = _filter_includes(args.only, resource_path.glob("*.mk"))
    if not files:
        raise EmptyResourceDir(resource_path)

    return sorted(files)


def _filter_includes(include_only, files: List[Path]) -> List[Path]:
    # Limit files so that only those in include_only (if present) are included
    # Normalize names to be case-insensitive and ignore mk suffix

    def norm(fname):
        return fname.replace(".mk", "").lower()

    to_include = {norm(fname) for fname in (include_only or [])}

    return [
        file for file in files if not to_include or norm(Path(file).name) in to_include
    ]


def _update_local_copy(args) -> None:
    repo = _repo_url(args)

    cached_repo = CACHE_DIR / Path(repo).name
    assert cached_repo.is_dir()

    cmd = f"cd {cached_repo} && git pull --force --rebase origin {args.branch}"

    _sys_exec(args, cmd)


def _cache_remote_repo(args) -> Path:
    # Cache repo locally if not present already
    repo = _repo_url(args)
    cached_repo = CACHE_DIR / Path(repo).name

    if not cached_repo.is_dir():
        _sys_exec(
            args,
            f"git clone {repo} {cached_repo} && cd {cached_repo} && git checkout --force {args.branch}",
        )

    return cached_repo


def _repo_url(args):
    if args.repo.startswith("git"):
        return args.repo

    return f"git@github.com:{args.repo}"


def _sys_exec(args, cmd, *, interactive=False):
    _debug(args)(f"exec {cmd}")
    opts = {"shell": True}
    if not args.debug and not interactive:
        opts["stderr"] = subprocess.DEVNULL
    if args.quiet:
        opts["stdout"] = subprocess.DEVNULL
    subprocess.run(cmd, **opts, check=True)


def _printer(args):
    if args.quiet:
        return lambda _, **kwargs: None
    return print


def _debug(args):
    if args.debug:
        return print
    return lambda _, **kwargs: None


def _fmt_notice(msg):
    return f"\u001b[33m{msg}\u001b[0m"


def _fmt_success(msg):
    return f"\u001b[32m{msg}\u001b[0m"


def _fmt_error(msg):
    return f"\u001b[31m{msg}\u001b[0m"


def compose(*fns):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), fns, lambda x: x)


if __name__ == "__main__":
    main()

### Unit tests


def test_filter_includes_not_being_set():
    assert _filter_includes(None, ["Common", "Rust", "Python"]) == [
        "Common",
        "Rust",
        "Python",
    ]


def test_filter_includes_with_multiple_values():
    assert _filter_includes(
        ["rust", "common"], ["Common.mk", "Rust.mk", "Python.mk"]
    ) == [
        "Common.mk",
        "Rust.mk",
    ]
