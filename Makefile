.PHONY: setup pipeline dashboard test

setup:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

pipeline:
	python load_data.py
	python analysis.py

dashboard:
	python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501

test:
	python -m pytest -q