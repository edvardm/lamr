include include/Python.mk
include include/Kubernetes.mk
include include/Common.mk
include include/Docker.mk

SRC ?= src
TESTS = $(SRC)/lamr.py
