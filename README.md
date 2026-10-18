# Formula 1 Podium Prediction - Milestone 1

Predict whether a recorded driver-race entry finishes on the podium using
information available after qualifying/final grid and before the race. The
notebook contains the data audit, three engineering answers, earlier-race
features, chronological splits, logistic regression/random forest/shallow NN,
experiments, SHAP/permutation explanations and complete/partial inference.

## Files

- `F1_Milestone1_Revised3.ipynb`: main notebook, saved with executed outputs.
- `F1_Milestone1_Report.pdf`: matching report from this repository's completed run.
- `requirements.txt`: pinned notebook and execution dependencies.
- `run_notebook.py`: executes the notebook in a fresh kernel and saves outputs
  only after the whole run succeeds.

The local `.venv/`, `archive/` data and generated `artifacts/` are ignored by Git.
The notebook contains its plots inline; reading the GitHub version does not
require those local folders.

## Run in VS Code on this computer

1. Open this repository folder in VS Code.
2. Open `F1_Milestone1_Revised3.ipynb`.
3. Use **Select Kernel > Python Environments** and select
   `.venv\Scripts\python.exe` from this folder.
4. Confirm the kernel label says **Python**, then select **Restart Kernel** and **Run All**.

If VS Code shows **SQL** or "No connection selected", use **Select Kernel >
Select Another Kernel > Python Environments** and choose the `.venv` Python
above. That message comes from the SQL extension; this notebook uses Python.
The workspace also opens `.ipynb` files with the Jupyter notebook editor.
See the [VS Code notebook guide](https://code.visualstudio.com/docs/datascience/jupyter-notebooks)
for the kernel picker and notebook controls.

All 14 dataset CSVs are already available locally in `archive/`. Code exports
tables, figures and fitted models to `artifacts/` by default. Execution may take
about 10-15 minutes on this machine. Use a fresh kernel for a complete rerun.

Alternatively, run all cells from a PowerShell terminal in this folder:

```powershell
.\.venv\Scripts\python.exe run_notebook.py
```

The runner records progress in `artifacts/execution_status.json`. A failed run
saves `artifacts/failed_execution.ipynb` for inspection and preserves the last
successful notebook in the repo root. A recovery copy of each successful run
is also kept in `artifacts/last_successful_execution.ipynb`. Avoid editing or
running the open notebook while the terminal runner is saving it.

## Set up a fresh clone

Install Python **3.12** and the Python/Jupyter extensions for VS Code. From the
repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Extract the supplied dataset ZIP so `archive/results.csv` and the other 13 CSVs
are directly inside `archive/`. This project uses the supplied 1950-2024 Kaggle/
Ergast snapshot; downloading a newer dataset can change results. To use another
local folder without copying data:

```powershell
.\.venv\Scripts\python.exe run_notebook.py --data 'D:\path\to\the\14-CSVs'
```

## Run on Kaggle

Import the `.ipynb`, attach the same Formula 1 dataset and use **Save Version >
Save & Run All**. The notebook supports the standard Kaggle dataset paths.
Kaggle can have different library versions, which can change numeric results.
Keep the executed notebook, its generated artifacts and its PDF report from
one run together.

Dataset: [Formula 1 World Championship](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020)

## Evaluation scope

Training uses 1950-2018, validation 2019-2021 and later-era evaluation 2022-2024.
All current choices use training/validation only. **The 2022-2024 period was
already viewed in earlier revisions**, so it is not a newly untouched holdout.
The notebook/report retain this limitation. Explanations are not causal effects.

The repository has not been published or pushed by the setup process. Once a
GitHub remote is configured, commit the notebook, matching PDF and small support
files, then publish the intended repository with the visibility required by the
course.

## Verified local execution

Run `20261018T210548Z` completed all **102 code cells** in 10.5 minutes with no saved cell errors. The notebook includes 51 plots, all 30 inference checks passed, and the report was checked against the same run. Model metrics match the prior audited execution within numerical precision. The analytical source is unchanged.
