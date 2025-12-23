.PHONY: install clean

install:
	./scripts/envinstall.sh

clean:
	rm -rf build/
	rm -rf dist/
	find src/ -type d -name '*.egg-info' -exec rm -rf {} +
	find src/ -type d -name __pycache__ -exec rm -rf {} +
	find src/ -type f -name "*.pyc" -delete
