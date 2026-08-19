# Analysis 1 -- the code that goes with the course.
#
#   make venv                once: .venv with marimo + matplotlib
#   make notebooks           export the notebooks to build/ as a static site
#   make serve               look at that export at localhost:8000
#   make run NB=lec01        run one notebook as an app, at native speed
#   make edit NB=lec01       open one notebook to write it
#   make clean               remove build/
#
# The experiments need none of this: they are standard library only.
#
#   python3 lec01_experiments.py

BUILD  ?= build
VENV   ?= .venv
MARIMO ?= $(VENV)/bin/marimo

NOTEBOOKS = $(wildcard notebooks/*.py)

.PHONY: venv notebooks serve run edit clean

venv:
	python3 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --quiet --upgrade pip
	$(VENV)/bin/python -m pip install --quiet marimo matplotlib
	@echo "-> $(VENV) ready; now: make notebooks"

# analysis.py is copied beside each exported notebook because in the browser
# there is no repository to import it from: the notebook fetches it over HTTP
# from its own directory.  Still one toolbox, just delivered differently.
notebooks:
	@rm -rf $(BUILD) && mkdir -p $(BUILD)
	@for nb in $(NOTEBOOKS); do \
	  name=$$(basename $$nb .py); \
	  echo "  exporting $$name"; \
	  $(MARIMO) export html-wasm $$nb -o $(BUILD)/$$name --mode run \
	      --no-show-code >/dev/null || exit 1; \
	  cp analysis.py $(BUILD)/$$name/; \
	done
	@printf '%s\n' \
	  '<!doctype html><meta charset="utf-8">' \
	  '<title>Analysis 1 - code</title>' \
	  '<style>body{font:16px/1.6 Georgia,serif;max-width:34em;margin:4em auto;padding:0 1em}' \
	  'a{display:block;padding:.4em 0}</style>' \
	  '<h1>Mathematical Analysis 1</h1>' \
	  '<p>Each page runs Python in your browser. Nothing to install; the first' \
	  'load takes a few seconds while the interpreter arrives.</p>' \
	  > $(BUILD)/index.html
	@for nb in $(NOTEBOOKS); do \
	  name=$$(basename $$nb .py); \
	  echo "<a href=\"$$name/\">$$name</a>" >> $(BUILD)/index.html; \
	done
	@echo "-> $(BUILD)/"

serve: notebooks
	@echo "-> http://localhost:8000"
	@python3 -m http.server 8000 --directory $(BUILD)

run:
ifndef NB
	$(error set NB, e.g. make run NB=lec01)
endif
	$(MARIMO) run notebooks/$(NB).py

edit:
ifndef NB
	$(error set NB, e.g. make edit NB=lec01)
endif
	$(MARIMO) edit notebooks/$(NB).py

clean:
	rm -rf $(BUILD)
