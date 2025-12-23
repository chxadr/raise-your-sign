#!/bin/sh

set -e

VENV_DIR=".venv"
PY_VERSION="3.13"

# Message colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Python version
printf "${GREEN}Checking Python ${PY_VERSION} version requirements ...${NC}\n"
if ! command -v python${PY_VERSION} >/dev/null 2>&1; then
    printf "${RED}Python ${PY_VERSION} not found${NC}\n"
    printf "${YELLOW}Consider installing Python ${PY_VERSION} first${NC}\n"
    exit 1
fi

# Create the virtual environment
printf "${GREEN}Creating Python virtual environment ...\n"
printf "\tPython version: ${PY_VERSION}\n"
printf "\tLocation: ${VENV_DIR}${NC}\n"
if ! python${PY_VERSION} -m venv ${VENV_DIR}; then
    printf "${RED}Failed to create Python virtual environment${NC}\n"
    if [ -d ${VENV_DIR} ]; then
        rm -r ${VENV_DIR}
    fi
    exit 1
fi
printf "${GREEN}Python virtual environment created at ${VENV_DIR}${NC}\n"

# Install requirements
if ! ${VENV_DIR}/bin/pip install -r requirements.txt; then
    printf "${RED}Failed to install requirements${NC}\n"
    printf "${YELLOW}Consider a manual installation of all dependencies\n"
    printf "\trun: source ${VENV_DIR}/bin/activate\n"
    printf "\trun: pip install <PACKAGE_NAME>==<VERSION>\n"
    printf "Or delete ${VENV_DIR}$ with rm -r ${VENV_DIR}${NC}\n"
    exit 1
fi
printf "${GREEN}Python virtual environment is ready to be used\n"
printf "To activate, run: source ${VENV_DIR}/bin/activate${NC}\n"
exit 0

