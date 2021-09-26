NOTEBOOK=ssg.ipynb

all: script readme

script:
	jupyter nbconvert --to script $(NOTEBOOK)
	python ssg.py

readme:
	jupyter nbconvert --to markdown $(NOTEBOOK) --output README
	
serve:
	@echo "http://localhost:8000/"
	python -m http.server -d build
