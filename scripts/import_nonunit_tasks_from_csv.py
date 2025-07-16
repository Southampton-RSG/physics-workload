"""
Imports tasks not associated with a unit from a cut-down version of the load_master tab of the spreadsheet

Needs to be run within the Django context; feed it into the management shell with:

    ```
    uv run manage.py shell < scripts/import_tasks_from_csv.py
    ```
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from logging import getLogger, Logger, INFO
from os import getcwd
from pathlib import Path

from pandas import DataFrame, read_csv, isnull

from django.conf import settings

from app.models import Task, AcademicGroup


# Set up logging
logger: Logger = getLogger(__name__)

# Hardcoded for ease of dealing with the manage.py shell.
CSV_PATH: Path = Path(getcwd()) / "spreadsheet_tasks_nonunit.csv"
logger.info(f"Importing tasks from: {CSV_PATH}")

# Track the history of creation
settings.SIMPLE_HISTORY_ENABLED = True

# Read the CSV
load_df: DataFrame = read_csv(CSV_PATH, header=0, index_col=False)

tasks_created: int = 0
history_date: datetime = datetime(
    year=2024, month=9, day=20, hour=0, minute=0, second=0,
    tzinfo=ZoneInfo("GMT")
)

for idx, row in load_df.iterrows():
    # Iterate through the dataframe, and for each row create a new task and save the details.
    try:
        task, created = Task.objects.get_or_create(
            pk=100+idx,
            academic_group=AcademicGroup.objects.get(code=row.academic_group) if not isnull(row.academic_group) else None,
            name=row.task_name,
            description=row.description,
            notes=row.notes,
            load_fixed=row.load_fixed if row.load_fixed != 912 else 0,
            is_full_time=True if row.load_fixed == 912 else False,
        )
        task._history_date = history_date
        task.save()
        tasks_created += created

    except Exception as e:
        logger.warning(
            f"Row {idx}: Failed to import: {e} - {row}"
        )

# Stop tracking history changes.
settings.SIMPLE_HISTORY_ENABLED = False

logger.info(
    f"Import complete, created {tasks_created} tasks."
)
