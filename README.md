# Experimental Techniques in Quantum Technology

## Requirements

- Python 3
- `numpy`, `pandas`, `matplotlib`, `ipykernel` (see [requirements.txt](requirements.txt))

## Setup

Create a virtual environment (`venv/`, git-ignored) and install dependencies:

```bash
make install
```

This builds `venv/` and installs everything from `requirements.txt`. All other
`make` targets automatically use the venv interpreter once it exists.

## Usage with make

```bash
make install     # create venv/ and install dependencies
make convert      # .dat -> .csv, only if a requested CSV is missing
make reconvert    # force re-conversion of all .dat files
make plot         # overlay CSV_FILES in a window (3-trace GUI view)
make plotall      # overlay every CSV in CSV_DIR
make save         # overlay CSV_FILES and save to PNG
make combine      # merge CSV_FILES into one wide CSV and save its plot
make clean        # delete the generated CSV_DIR
make help         # list targets and current variable values
```

Variables can be overridden on the command line, e.g.:

```bash
make plot CSV_FILES="1.csv 2.csv 3.csv"
make convert CURVE_DIR=/path/to/curve
```

Key variables: `CURVE_DIR`, `CSV_DIR`, `CSV_FILES`, `PNG`, `COMBINED`
(run `make help` to see their current values).

