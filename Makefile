.PHONY: install build run clean

install:
	./scripts/envinstall.sh

build:
	cd main/ && pyinstaller main.spec

run:
	cd main/dist/ && ./quiz &

clean:
	find src/ -type d -name 'build' -exec rm -rf {} +
	find src/ -type d -name 'dist' -exec rm -rf {} +
	find src/ -type d -name '*.egg-info' -exec rm -rf {} +
	find src/ -type d -name __pycache__ -exec rm -rf {} +
	find src/ -type f -name "*.pyc" -delete
