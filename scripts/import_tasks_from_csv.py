"""
Imports tasks from the load_master tab of the spreadsheet

Needs to be run within the Django context; feed it into the management shell with:

    ```
    uv run manage.py shell < scripts/import_tasks_from_csv.py
    ```

Annoyingly, because of this the path has to be hardcoded.

DOESN'T WORK
This is simply too complex a file to import.
"""
from datetime import datetime
from logging import getLogger, Logger
from pathlib import Path

import pandas
from pandas import DataFrame, read_csv, isnull, to_numeric
from django.conf import settings
from app.models import Unit, Task


# Set up logging
logger: Logger = getLogger(__name__)

# Hardcoded for ease of dealing with the manage.py shell.
CSV_PATH: str = Path("~/physics-workload/spreadsheet_load_master.csv")
logger.info(f"Importing tasks from: {CSV_PATH}")

# Track the history of creation
settings.SIMPLE_HISTORY_ENABLED = True


# Read the staff CSV, and convert the empty cells to 0.
load_df: DataFrame = read_csv(CSV_PATH, header=0, index_col=False)
load_df.info()
# load_df = load_df.fillna(0)
# load_df[].fillna(0, inplace=True)
load_df.rename(
    columns={
        'Deputy /Assessors etc': 'hours_fixed_deputy',
        'Number of Synoptic lectures': 'synoptic_lectures',
        'Number of Lectures/Problems Classes Run by Coordinator': 'lectures',
        'Coursework (number of items prepared)': 'coursework',
        'Coursework (fraction of module mark)': 'coursework_mark_fraction',
        'Fraction of Courseowork marked by coordinator': 'task_coursework_fraction',
        'Examination (fraction of module mark)': 'exam_mark_fraction',
        'Fraction of Examination marked by coordinator': 'task_exam_fraction',
        'Total Number of CATS': 'credits',
        'Task Description': 'task_name',
        'Number of Students': 'students',
        'Description/Unit title': 'unit_name',
        'Task Category/Unit Code': 'code',
        'Unit co-ord load': 'load',
        'lst time unit co-ord load': 'load_first',
        load_df.columns[17]: 'notes'
    },
    inplace=True
)

logger.info("Strip trailing whitespace")
for column in load_df.columns:
    if load_df[column].dtype == 'object':
        load_df[column] = load_df[column].str.strip()

    load_df[load_df[column] == ''] = None

logger.info("Convert raw numbers columns to ints")
for column in [
    'hours_fixed_deputy', 'synoptic_lectures', 'coursework', 'credits', 'students', 'lectures'
]:
    load_df[column] = to_numeric(load_df[column], errors='coerce')
    load_df[column] = load_df[column].fillna(0)

logger.info("Convert fraction columns to floats")
for column in [
    'exam_mark_fraction', 'coursework_mark_fraction',
    'task_coursework_fraction', 'task_exam_fraction',
]:
    equation_rows = load_df[column].str.contains('=').fillna(False)
    load_df[column][equation_rows] = load_df[column][equation_rows].str.lstrip('=').apply(pandas.eval)
    percentage_rows = load_df[column].str.contains('%').fillna(False)
    load_df[column][percentage_rows] = load_df[column][percentage_rows].str.rstrip('%').astype('float')/100.0


for idx, row in load_df.iterrows():
    # Iterate through the dataframe, and for each row create a new unit and save the details.
    code: str = row.code

    if isnull(code) or not code or (code[:4] != "PHYS" and code[:4] != "OPTO"):
        # Skip this line if it's not a valid unit code
        continue
    else:
        logger.debug(
            f"\nImporting row {idx}: {row.code}"
        )

    try:
        # Try and find this task's unit
        unit: Unit = Unit.objects.get(code=code)

    except Unit.DoesNotExist:
        logger.info(
            f"No unit with code: {code}"
        )
        continue

    try:
        # Try and find this task
        task: Task = Task.objects.get(unit=unit, name=row.task_name)
    except Task.DoesNotExist:
        try:
            task = (Task.objects.get(unit=unit, name="Co-ordinator"))
            continue

        except Task.DoesNotExist:
            logger.info(
                f"No existing task with name: {row.task_name} or 'Co-ordinator', creating new one"
            )

    try:
        if str(row.load)[0] == '=':
            # If this is an equation, then we need to use the equation details
            task: Task = Task(
                unit=unit,
                name=row.task_name if row.task_name else "Co-ordinator",
                description=row.comments,
                notes=row.comments,
                students=row.students if not isnull(row.students) and row.students != unit.students else None,
                coursework_fraction=row.task_coursework_fraction if not isnull(row.task_coursework_fraction) else None,
                exam_fraction=row.task_exam_fraction if not isnull(row.task_exam_fraction) else None,
                load_fixed=float(row.load.split('+')[-1]),
                load_fixed_first=float(row.load_first.split('+')[-1])
            )
            task._history_date = datetime(year=2024, month=9, day=20, hour=0, minute=0, second=0)
            task.save()

        else:
            task: Task = Task(
                unit=unit,
                name=row.task_name if row.task_name else "Co-ordinator",
                description=row.comments,
                notes=row.comments,
                students=row.students if not isnull(row.students) and row.students != unit.students else None,
                coursework_fraction=row.task_coursework_fraction if not isnull(row.task_coursework_fraction) else None,
                exam_fraction=row.task_exam_fraction if not isnull(row.task_exam_fraction) else None,
                load_fixed=float(row.load),
                load_fixed_first=float(row.load_first)
            )
            task._history_date = datetime(year=2024, month=9, day=20, hour=0, minute=0, second=0)
            task.save()

    except:
        logger.warning(
            f"Row {idx}: Failed to import, must do manually."
        )

# Stop tracking history changes.
settings.SIMPLE_HISTORY_ENABLED = False

logger.info("Import complete")
