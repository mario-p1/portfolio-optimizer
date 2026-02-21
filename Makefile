.PHONY:
dev:
	uv run python -m streamlit run portfolio_optimizer/streamlit_app.py --server.address 127.0.0.1 --server.runOnSave true