PYTHON    ?= python
CONVERT   ?= dat_to_csv.py
PLOT      ?= plot_curve.py

CURVE_DIR ?= $(HOME)/pyrpl_user_dir/curve
CSV_DIR   ?= $(CURVE_DIR)/csv

# The channel files to plot together (in1 / in2 / cross)
CSV_FILES ?= 1.csv 2.csv 3.csv

PNG       ?= $(CSV_DIR)/plot.png
COMBINED  ?= $(CSV_DIR)/combined.csv

CSV_PATHS := $(addprefix $(CSV_DIR)/,$(CSV_FILES))

.PHONY: all convert reconvert plot plotall save combine clean help

define ENSURE_CSV
	@for f in $(CSV_PATHS); do \
	  if [ ! -e "$$f" ]; then \
	    echo ">> CSV missing ($$f) - converting"; \
	    $(PYTHON) $(CONVERT) $(CURVE_DIR) $(CSV_DIR); \
	    break; \
	  fi; \
	done
endef

all: plot

# Convert only if a requested CSV is missing
convert:
	$(ENSURE_CSV)
	@echo "CSVs ready in $(CSV_DIR)"

# Force re-conversion
reconvert:
	$(PYTHON) $(CONVERT) $(CURVE_DIR) $(CSV_DIR)

# Overlay CSV_FILES in a window (in1=blue, in2=green, cross=magenta)
plot:
	$(ENSURE_CSV)
	$(PYTHON) $(PLOT) $(CSV_PATHS)

# Overlay every CSV in CSV_DIR
plotall:
	$(ENSURE_CSV)
	$(PYTHON) $(PLOT) $(CSV_DIR)

# Overlay CSV_FILES, save the figure to PNG
save:
	$(ENSURE_CSV)
	$(PYTHON) $(PLOT) $(CSV_PATHS) $(PNG)

# Merge CSV_FILES into ONE wide CSV (COMBINED) and save its plot
combine:
	$(ENSURE_CSV)
	$(PYTHON) $(PLOT) $(CSV_PATHS) $(PNG) --combine $(COMBINED)

clean:
	rm -rf $(CSV_DIR)

help:
	@echo "Targets:"
	@echo "  make plot      - overlay CSV_FILES in a window (3-trace GUI view)"
	@echo "  make save      - overlay CSV_FILES, save to PNG"
	@echo "  make combine   - merge CSV_FILES into one wide CSV ($(notdir $(COMBINED)))"
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
	@echo "  COMBINED  = $(COMBINED)"
