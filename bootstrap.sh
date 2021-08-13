#!/usr/bin/env bash

set -eu -o pipefail

URL=https://raw.githubusercontent.com/edvardm/lamr

TMP=${TMPDIR:-/tmp}
LAMR_INSTALL_DIR=${HOME}/.local/bin
INSTALL=${INSTALL:-$LAMR_INSTALL_DIR}
LAMR_BIN=${INSTALL}/lamr

download_pyscript() {
    outfile=$1
    lamr_url="${URL}/master/src/lamr.py"
    echo "Downloading LAMR from ${lamr_url}..."

    curl -ssL "${lamr_url}" -o "${outfile}"
}

install_pyscript() {
    # tr is for trimming dup slashes from tmp path if present
    tmp=$(echo "$TMP/lamr.py" | tr -s /)

    download_pyscript "${tmp}"
    test -f "${tmp}" || (echo "Download failed" && exit 1)

    echo "Installing LAMR to ${INSTALL}"
    install "${tmp}" "${LAMR_BIN}"
}

echo "Executing bootstrap script..."
install_pyscript
myname=$(basename "$0")

echo "Bootstrap complete"
echo
echo "In order to use lamr conveniently, ensure that directory ${INSTALL} is in your PATH by putting"
echo
echo "  export PATH=${INSTALL}:\$PATH"
echo
echo "to your ~/.zshrc or ~/.bashrc"
echo
echo "It is recommended that you add ./${myname} to version control, so that it is easy to setup for other users."
echo
echo "Next run '${LAMR_BIN} install --repo <makefile repository url>' to install project Makefiles."
