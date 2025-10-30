"""
Imports tasks not associated with a unit from a cut-down version of the load_master tab of the spreadsheet

Needs to be run within the Django context; feed it into the management shell with:

    ```
    uv run manage.py shell < scripts/import_tasks_from_csv.py
    ```
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from logging import getLogger, Logger
from os import getcwd
from pathlib import Path

from pandas import DataFrame, isnull

from django.conf import settings

from app.models import Task, AcademicGroup
from load_tasks import load_nonunit_tasks_from_load_master_csv


# Set up logging
logger: Logger = getLogger(__name__)

# Hardcoded for ease of dealing with the manage.py shell.
CSV_FILES: dict[int, Path] = {
    2024: Path(getcwd() + "spreadsheet_tasks_nonunit_2024.csv"),
    2025: Path(getcwd() + "spreadsheet_tasks_nonunit_2025.csv"),
}

def import_nonunit_tasks(path: Path, year: int, initial_pk: int) -> int:
    """
    Imports tasks not associated with a unit from a cut-down version of the load_master, and adds them to the DB.

    :param path: The path to the spreadsheet file
    :param year: The year the file is for (2024 for 2024/2025).
    :param initial_pk: The first PK to assign.
    :return: The PK of the last task created.
    """
    logger.info(f"Importing tasks for: {year}, path: {path}")

    # Track the history of creation
    settings.SIMPLE_HISTORY_ENABLED = True

    # Read the CSV
    load_df: DataFrame = load_nonunit_tasks_from_load_master_csv(path)

    tasks_created: int = 0
    history_date: datetime = datetime(
        year=year, month=9, day=20, hour=0, minute=0, second=0,
        tzinfo=ZoneInfo("GMT"),
    )

    for idx, row in load_df.iterrows():
        # Iterate through the dataframe, and for each row create a new task and save the details.
        try:
            task, created = Task.objects.get_or_create(
                pk=initial_pk+idx,
                academic_group=AcademicGroup.objects.get(code=row.academic_group) if not isnull(row.academic_group) else None,
                title=row.task_name,
                description=row.description,
                notes=row.notes,
                load_fixed=row.load_fixed if row.load_fixed != -1 else None,
                load_fixed_first=row.load_fixed_first,
                is_full_time=(row.load_fixed == -1),
            )
            task._history_date = history_date
            task.save()
            tasks_created += created

        except Exception as e:
            logger.warning(
                f"Row {idx}: Failed to import: {e} - {row}"
            )

        logger.info(f"Imported tasks for: {year}, created: {tasks_created}")

        # Stop tracking history changes.
        settings.SIMPLE_HISTORY_ENABLED = False

        return len(load_df) + initial_pk


def main():
    """
    Runs the import for the hard-coded files.
    """
    logger.info(
        f"Importing non-unit tasks: {CSV_FILES}"
    )
    initial_pk: int = 0

    for year, path in CSV_FILES.items():
        initial_pk = import_nonunit_tasks(path, year, initial_pk)
