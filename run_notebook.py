"""Execute the project in a fresh kernel using this Python environment.

Usage: .\.venv\Scripts\python.exe run_notebook.py
The notebook is replaced with executed outputs only after every cell succeeds.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import time
import traceback
import uuid

import nbformat
from nbclient import NotebookClient
from jupyter_client import AsyncKernelManager


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=root / 'archive')
    parser.add_argument('--output-dir', type=Path, default=root / 'artifacts')
    args = parser.parse_args()
    data_dir, output_dir = args.data.resolve(), args.output_dir.resolve()
    if sys.version_info[:2] != (3, 12):
        parser.error('Use the Python 3.12 environment described in README.md.')
    if not (data_dir / 'results.csv').is_file():
        parser.error('Extract all 14 dataset CSVs into archive/ or pass --data PATH.')

    notebook_path = root / 'F1_Milestone1_Revised3.ipynb'
    notebook = nbformat.read(notebook_path, as_version=4)
    nbformat.validate(notebook)
    source_hash = hashlib.sha256(json.dumps(
        [(c.cell_type, c.source) for c in notebook.cells], ensure_ascii=False
    ).encode('utf-8')).hexdigest()
    code_count = sum(c.cell_type == 'code' for c in notebook.cells)
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.execution_count = None
            cell.outputs = []

    runtime = output_dir / '.runtime'
    runtime.mkdir(parents=True, exist_ok=True)
    for env, name in [('MPLCONFIGDIR', 'matplotlib'), ('IPYTHONDIR', 'ipython')]:
        folder = runtime / name
        folder.mkdir(exist_ok=True)
        os.environ[env] = str(folder)
    os.environ['F1_DATA_DIR'] = str(data_dir)
    os.environ['F1_OUTPUT_DIR'] = str(output_dir)
    os.environ['MPLBACKEND'] = 'module://matplotlib_inline.backend_inline'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['JUPYTER_PLATFORM_DIRS'] = '1'
    started = time.monotonic()
    progress = []
    begin_times = {}

    def status(completed=False, error=None):
        payload = {'completed': completed, 'executed_code_cells': len(progress),
                   'expected_code_cells': code_count,
                   'elapsed_seconds': time.monotonic() - started, 'cells': progress}
        if error:
            payload['error'] = error
        (output_dir / 'execution_status.json').write_text(
            json.dumps(payload, indent=2), encoding='utf-8')

    def on_execute(cell, cell_index, **kwargs):
        if cell.cell_type == 'code':
            begin_times[cell_index] = time.monotonic()
            print(f'Running code cell {len(progress) + 1}/{code_count} '
                  f'(notebook cell {cell_index + 1})', flush=True)

    def on_executed(cell, cell_index, **kwargs):
        if cell.cell_type != 'code':
            return
        errors = [o for o in cell.outputs if o.output_type == 'error']
        progress.append({'notebook_cell': cell_index + 1,
                         'execution': cell.execution_count,
                         'passed': not errors,
                         'seconds': time.monotonic() - begin_times[cell_index]})
        status()
        print(f'Finished {len(progress)}/{code_count} '
              f'in {progress[-1]["seconds"]:.2f}s', flush=True)

    # Use this environment's Python even if another python3 kernel is registered.
    manager = AsyncKernelManager(kernel_name='python3',
        connection_file=str(runtime / f'kernel-{uuid.uuid4().hex}.json'))
    manager.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher',
                                '-f', '{connection_file}']
    client = NotebookClient(notebook, km=manager, timeout=1800,
        resources={'metadata': {'path': str(root)}},
        on_cell_execute=on_execute, on_cell_executed=on_executed)
    print('Python:', sys.executable, flush=True)
    print('Dataset:', data_dir, flush=True)
    try:
        client.execute()
        code = [c for c in notebook.cells if c.cell_type == 'code']
        assert [c.execution_count for c in code] == list(range(1, code_count + 1))
        assert not [o for c in code for o in c.outputs if o.output_type == 'error']
        nbformat.validate(notebook)
        temp = notebook_path.with_suffix('.executed.tmp.ipynb')
        nbformat.write(notebook, temp)
        temp.replace(notebook_path)
        manifest_path = output_dir / 'run_manifest.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest.update(notebook_source_sha256=source_hash,
            notebook_sha256=hashlib.sha256(notebook_path.read_bytes()).hexdigest(),
            executed_code_cells=code_count,
            fresh_execution_seconds=time.monotonic() - started)
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        status(completed=True)
    except BaseException as error:
        nbformat.write(notebook, output_dir / 'failed_execution.ipynb')
        status(error=f'{type(error).__name__}: {error}')
        raise
    finally:
        # An explicitly supplied manager is owned by this script, not nbclient.
        if manager.has_kernel:
            from jupyter_core.utils import run_sync
            run_sync(manager.shutdown_kernel)(now=True)
            run_sync(manager.cleanup_resources)()
    print(f'Completed all {code_count} code cells in '
          f'{time.monotonic() - started:.1f}s. Saved {notebook_path.name}.', flush=True)


if __name__ == '__main__':
    main()
