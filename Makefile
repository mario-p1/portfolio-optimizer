.PHONY:
dev:
	uv run python -m streamlit run Home.py --server.address 127.0.0.1 --server.runOnSave true