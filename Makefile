setup:
	python3.8 -m pip install poetry
	poetry env use python3.8
	poetry run pip install --upgrade pip
minimum-requirements:
  poetry export --without-hashes --with-credentials -f requirements.txt | grep -e ml3-repo-manager -e pyyaml -e -- > requirements.txt
