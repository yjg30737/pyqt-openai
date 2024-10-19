.PHONY: venv run clean format build upload install

ifeq ($(OS),Windows_NT)
    PYTHON=python
    VE_PYTHON=venv\Scripts\python
    VE_PIP=venv\Scripts\pip
    VE_BLACK=venv\Scripts\black
    VE_TWINE=venv\Scripts\twine
    VE_PYINSTALLER=venv\Scripts\pyinstaller
else
    PYTHON=python3
    VE_PYTHON=venv/bin/python
    VE_PIP=venv/bin/pip
    VE_BLACK=venv/bin/black
    VE_TWINE=venv/bin/twine
    VE_PYINSTALLER=venv/bin/pyinstaller
endif

venv:
	$(PYTHON) -m venv venv
	$(VE_PIP) install -r requirements.txt

run:
	$(VE_PYTHON) pyqt_openai/main.py

clean:
	rm -rf dist/ build/ *.egg-info

format:
	$(VE_BLACK) .

build:
	$(VE_PYTHON) -m build

upload: build
	$(VE_TWINE) upload dist/*

install:
	$(VE_PYINSTALLER) main.spec
