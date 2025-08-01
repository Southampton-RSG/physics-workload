"""
Imports Units from the Load Master tab of the spreadsheet

Needs to be run within the Django context; feed it into the management shell with:

    ```
    uv run manage.py shell < scripts/import_unit_tasks_from_csv.py
    ```
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from logging import getLogger, Logger, DEBUG, INFO, WARNING, ERROR, CRITICAL
from os import getcwd
from pathlib import Path

import pandas
from pandas import DataFrame, read_csv, isnull, to_numeric
from django.conf import settings
from app.models import Unit, Task, AcademicGroup, Staff, Assignment

# Set up logging
logger: Logger = getLogger(__name__)
# logger.propagate = True

# Hardcoded for ease of dealing with the manage.py shell.
CSV_PATH: Path = Path(getcwd()) / "spreadsheet_tasks_unit.csv"
logger.info(f"Importing modules from: {CSV_PATH}")

# Track the history of creation
settings.SIMPLE_HISTORY_ENABLED = True
history_date: datetime = datetime(
    year=2024, month=9, day=20, hour=0, minute=0, second=0,
    tzinfo=ZoneInfo("GMT")
)

# Read the staff CSV, and convert the empty cells to 0.
load_df: DataFrame = read_csv(CSV_PATH, header=0, index_col=False)
load_df.rename(
    columns={
        'STAFF': 'staff_name',
        'TASK CAT/UNIT CODE': 'code',
        'TASK DETAIL': 'task_name',
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
    # None yet
]:
    load_df[column] = to_numeric(load_df[column], errors='coerce')
    load_df[column] = load_df[column].fillna(0)

logger.info("Convert fraction columns to floats")
for column in [
    # None
]:
    equation_rows = load_df[column].str.contains('=').fillna(False)
    load_df.loc[equation_rows, column] = load_df.loc[equation_rows, column].str.lstrip('=').apply(pandas.eval)
    percentage_rows = load_df[column].str.contains('%').fillna(False)
    load_df.loc[percentage_rows, column] = load_df.loc[percentage_rows, column].str.rstrip('%').astype('float')/100.0

# Track what's made
assignments_created: int = 0
history_date: datetime = datetime(year=2024, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))

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
        # Skip this line if the unit's already been created
        unit: Unit = Unit.objects.get(code=code)
        logger.info(
            f"Found {code}: {row.name}"
        )
    except Unit.DoesNotExist:
        continue

    try:
        # Skip this if the staff can't be found
        staff: Staff = Staff.objects.get(name=row.staff_name)
        logger.info(
            f"Found staff: {staff}: {row.staff_name}"
        )
    except Staff.DoesNotExist:
        logger.info(
            f"No staff named: {row.staff_name}"
        )
        continue

    if str(row.task_name).lower() == "coord":
        try:
            task: Task = Task.objects.get(unit=unit, is_lead=True)
            logger.info(
                f"Found existing lead task: {task}"
            )
        except Task.DoesNotExist:
            continue

        assignment, created = Assignment.objects.get_or_create(
            task=task,
            staff=staff,
            is_first_time=False,
            is_provisional=True,
        )
        assignment._history_date = history_date
        assignment.save()
        assignments_created += created

    elif str(row.task_name).lower() == "deputy":
        try:
            task: Task = Task.objects.get(unit=unit, title="Deputy Lead")
            logger.info(
                f"Found existing deputy lead task: {task}"
            )
        except Task.DoesNotExist:
            continue

        assignment, created = Assignment.objects.get_or_create(
            task=task,
            staff=staff,
            is_first_time=False,
            is_provisional=True,
        )
        assignment._history_date = history_date
        assignment.save()
        assignments_created += created

    else:
        continue

# Stop tracking history changes.
settings.SIMPLE_HISTORY_ENABLED = False

logger.info(
    f"Import complete. Created {assignments_created} assignments"
)
