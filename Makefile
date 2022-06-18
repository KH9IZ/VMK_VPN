deploy:
	# Add deadsnake repo if ubuntu lower then 22
	sudo apt install python3.10 python3.10-venv python3.10-dev

lint:
	pylint *.py --disable=unspecified-encoding,too-few-public-methods,unspecified-encoding --max-line-length=110
	pydocstyle *.py

test:
	python -m unittest discover
