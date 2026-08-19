.PHONY: install reproduce notebook test audit web

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

reproduce:
	python run_all.py

notebook:
	python tools/render_notebook.py

test:
	python -m pytest -q

audit:
	python tools/verify_repository.py

web:
	python -m streamlit run app.py
