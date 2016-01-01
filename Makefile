VENV = env/.built
PYTHON = env/bin/python3

all: test

$(VENV) env: env.sh
	sh env.sh
	touch $(VENV)

test: $(VENV)
	$(PYTHON) test_templet.py

clean:
	rm -rf pypy*
	rm *.pyc
	rm -rf __pycache__
	rm -rf env
