"""
Imports tasks not associated with a unit from a cut-down version of the load_master tab of the spreadsheet

Needs to be run within the Django context; feed it into the management shell with:

    ```
    uv run manage.py shell < scripts/import_tasks_from_csv.py
    ```
"""
from datetime import datetime
from logging import getLogger, Logger, INFO
from os import getcwd
from pathlib import Path

import pandas
from pandas import DataFrame, read_csv, isnull, to_numeric
from django.conf import settings
from app.models import Unit, Task, AcademicGroup

# Set up logging
logger: Logger = getLogger(__name__)
logger.setLevel(INFO)
logger.propagate = False

# Hardcoded for ease of dealing with the manage.py shell.
CSV_PATH: str = Path(getcwd()) / "spreadsheet_tasks_nonunit.csv"
logger.info(f"Importing tasks from: {CSV_PATH}")

# Track the history of creation
settings.SIMPLE_HISTORY_ENABLED = True

# Read the CSV
load_df: DataFrame = read_csv(CSV_PATH, header=0, index_col=False)
load_df.info()

tasks_created: int = 0

for idx, row in load_df.iterrows():
    # Iterate through the dataframe, and for each row create a new task and save the details.
    try:
        # Try and find this task's unit
        task: Task = Task.objects.get(pk=row.pk)
        continue

    except Task.DoesNotExist:
        logger.info(
            f"No task with key: {row.pk}, creating new."
        )

    try:
        # If this is an equation, then we need to use the equation details
        task: Task = Task(
            academic_group=AcademicGroup.objects.get(code=row.academic_group) if not isnull(row.academic_group) else None,
            name=row.task_name,
            description=row.description,
            notes=row.notes,
            load_fixed=row.load_fixed,
        )
        task._history_date = datetime(year=2024, month=9, day=20, hour=0, minute=0, second=0)
        task.save()
        tasks_created += 1

    except Exception as e:
        logger.warning(
            f"Row {idx}: Failed to import: {e}"
        )

# Stop tracking history changes.
settings.SIMPLE_HISTORY_ENABLED = False

logger.info(
    f"Import complete, created {tasks_created} tasks."
)
