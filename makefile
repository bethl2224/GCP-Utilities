SRC_DIR = .
PYTHON = python3
COVERGAGE = coverage
test:
	$(PYTHON) -m unittest discover -s gcp-mock-test -p "*.py" -v
	find . -name '*.pyc' -delete

coverage:
	$(PYTHON) -m coverage run -m unittest discover -s gcp-mock-test -p "*.py"
	$(PYTHON) -m coverage report

upgrade_req:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install --upgrade -r requirements.txt