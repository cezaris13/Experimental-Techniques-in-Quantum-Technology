# ============================================================================
#  PyRPL spectrum-analyzer curves:  .dat  ->  .csv  ->  plot
#  Override any variable on the command line, e.g.:
#      make CSV_FILE=7.csv
#      make CURVE_DIR=/data/run1 plot
# ============================================================================

# Python interpreter
PYTHON    ?= python

# Scripts
CONVERT   ?= dat_to_csv.py
PLOT      ?= plot_curve.py

# Folder holding the .dat files
CURVE_DIR ?= $(HOME)/pyrpl_user_dir/curve

# Where .csv files are written
CSV_DIR   ?= $(CURVE_DIR)/csv

# Which curve to plot
# test change
CSV_FILE  ?= 20.csv

# Full paths (do not edit)
CSV_PATH  := $(CSV_DIR)/$(CSV_FILE)
PNG       := $(CSV_DIR)/$(basename $(CSV_FILE)).png
DAT_FILES := $(wildcard $(CURVE_DIR)/*.dat)
STAMP     := $(CSV_DIR)/.converted

.PHONY: all convert plot save clean help

# Default: convert everything, then plot CSV_FILE
all: plot

# Convert all .dat -> .csv (re-runs only if a .dat or the script changed)
$(STAMP): $(CONVERT) $(DAT_FILES)
	$(PYTHON) $(CONVERT) $(CURVE_DIR) $(CSV_DIR)
	@touch $@

convert: $(STAMP)

# Plot CSV_FILE in a window (converts first if needed)
plot: $(STAMP)
	$(PYTHON) $(PLOT) $(CSV_PATH)

# Same plot, saved to PNG instead of shown
save: $(STAMP)
	$(PYTHON) $(PLOT) $(CSV_PATH) $(PNG)

# Delete generated CSVs/PNGs
clean:
	rm -rf $(CSV_DIR)

help:
	@echo "Targets:"
	@echo "  make convert   - convert all .dat in CURVE_DIR to .csv in CSV_DIR"
	@echo "  make plot      - convert (if needed) then plot CSV_FILE in a window"
	@echo "  make save      - convert (if needed) then save the plot to PNG"
	@echo "  make clean     - delete the CSV_DIR"
	@echo ""
	@echo "Variables (override like 'make CSV_FILE=7.csv'):"
	@echo "  PYTHON    = $(PYTHON)"
	@echo "  CURVE_DIR = $(CURVE_DIR)"
	@echo "  CSV_DIR   = $(CSV_DIR)"
	@echo "  CSV_FILE  = $(CSV_FILE)"
	@echo "  CSV_PATH  = $(CSV_PATH)"
