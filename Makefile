.PHONY: docs
init:
	python -m pip install --upgrade pip
	python -m pip install -r ./requirements.txt --upgrade
	python -m pip install build setuptools wheel flake8 --upgrade
build:
	python -m build
ci:
	python -m flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	python -m flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
	python setup.py install