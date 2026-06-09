PYTHON    ?= python3
VENV      ?= venv
VENV_PY   := $(VENV)/bin/python
PIP       := $(VENV)/bin/pip
CONVERT   ?= dat_to_csv.py
PLOT      ?= plot_curve.py

CURVE_DIR ?= $(HOME)/pyrpl_user_dir/curve
CSV_DIR   ?= $(CURVE_DIR)/csv

# The channel files to plot together (in1 / in2 / cross)
CSV_FILES ?= 1.csv 2.csv 3.csv

PNG       ?= $(CSV_DIR)/plot.png

CSV_PATHS := $(addprefix $(CSV_DIR)/,$(CSV_FILES))

# Use the venv interpreter if it exists, otherwise fall back to system python
RUN_PY := $(if $(wildcard $(VENV_PY)),$(VENV_PY),$(PYTHON))

.PHONY: all install convert reconvert plot plotall save clean help

define ENSURE_CSV
	@for f in $(CSV_PATHS); do \
	  if [ ! -e "$$f" ]; then \
	    echo ">> CSV missing ($$f) - converting"; \
	    $(RUN_PY) $(CONVERT) $(CURVE_DIR) $(CSV_DIR); \
	    break; \
	  fi; \
	done
endef

all: plot

# Create a virtual environment and install all project dependencies
install: $(VENV_PY)

$(VENV_PY): requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo ">> venv ready - run 'source $(VENV)/bin/activate' or just use 'make plot'"

# Convert only if a requested CSV is missing
convert:
	$(ENSURE_CSV)
	@echo "CSVs ready in $(CSV_DIR)"

# Force re-conversion
reconvert:
	$(RUN_PY) $(CONVERT) $(CURVE_DIR) $(CSV_DIR)

# Overlay CSV_FILES in a window (in1=blue, in2=green, cross=magenta)
plot:
	$(ENSURE_CSV)
	$(RUN_PY) $(PLOT) $(CSV_PATHS)

# Overlay every CSV in CSV_DIR
plotall:
	$(ENSURE_CSV)
	$(RUN_PY) $(PLOT) $(CSV_DIR)

# Overlay CSV_FILES, save the figure to PNG
save:
	$(ENSURE_CSV)
	$(RUN_PY) $(PLOT) $(CSV_PATHS) $(PNG)

clean:
	rm -rf $(CSV_DIR)

help:
	@echo "Targets:"
	@echo "  make install   - create $(VENV)/ and install all project dependencies"
	@echo "  make plot      - overlay CSV_FILES in a window (3-trace GUI view)"
	@echo "  make save      - overlay CSV_FILES, save to PNG"
	@echo "  make plotall   - overlay every CSV in CSV_DIR"
	@echo "  make convert   - .dat -> .csv only if a requested CSV is missing"
	@echo "  make reconvert - force re-conversion"
	@echo "  make clean     - delete CSV_DIR"
	@echo ""
	@echo "Variables (override like 'make CSV_FILES=\"1.csv 2.csv 3.csv\"'):"
	@echo "  PYTHON    = $(PYTHON)"
	@echo "  CURVE_DIR = $(CURVE_DIR)"
	@echo "  CSV_DIR   = $(CSV_DIR)"
	@echo "  CSV_FILES = $(CSV_FILES)"
	@echo "  PNG       = $(PNG)"
