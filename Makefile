.PHONY: venv clean format build upload install

venv:
	python -m venv venv
ifeq ($(OS),Windows_NT)
	venv\Scripts\activate
else
	. venv/bin/activate
endif
	pip install -r requirements.txt

clean:
	rm -rf dist/ build/ *.egg-info

format:
	black .

build:
	python -m build

upload: build
	twine upload dist/*

install:
	pyinstaller main.spec