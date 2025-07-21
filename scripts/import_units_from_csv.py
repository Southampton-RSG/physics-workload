"""
Imports Units from the Load Master tab of the spreadsheet

Needs to be run within the Django context; feed it into the management shell with:

    ```
    uv run manage.py shell < scripts/import_units_from_csv.py
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
from app.models import Unit, Task, AcademicGroup

# Set up logging
logger: Logger = getLogger(__name__)
# logger.propagate = True

# Hardcoded for ease of dealing with the manage.py shell.
CSV_PATH: Path = Path(getcwd()) / "spreadsheet_load_master.csv"
logger.info(f"Importing units from: {CSV_PATH}")

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
        'Deputy /Assessors etc': 'hours_fixed_deputy',
        'Number of Synoptic lectures': 'synoptic_lectures',
        'Number of Lectures/Problems Classes Run by Coordinator': 'lectures',
        'Coursework (number of items prepared)': 'coursework',
        'Coursework (fraction of module mark)': 'coursework_mark_fraction',
        'Fraction of Courseowork marked by coordinator': 'task__coursework_fraction',
        'Examination (fraction of module mark)': 'exam_mark_fraction',
        'Fraction of Examination marked by coordinator': 'task__exam_fraction',
        'Total Number of CATS': 'credits',
        'Task Description': 'task__name',
        'Number of Students': 'students',
        'Description/Unit title': 'unit_name',
        'Task Category/Unit Code': 'code',
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
    'task__coursework_fraction', 'task__exam_fraction',
]:
    equation_rows = load_df[column].str.contains('=').fillna(False)
    load_df.loc[equation_rows, column] = load_df.loc[equation_rows, column].str.lstrip('=').apply(pandas.eval)
    percentage_rows = load_df[column].str.contains('%').fillna(False)
    load_df.loc[percentage_rows, column] = load_df.loc[percentage_rows, column].str.rstrip('%').astype('float')/100.0

# Track what's made
units_created: int = 0
tasks_created: int = 0
history_date: datetime = datetime(year=2024, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo('GMT'))

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
            f"Already found {code}: {row.name}"
        )
        continue

    except Unit.DoesNotExist:
        logger.info(
            f"Creating new unit: {code} - {row.unit_name}"
        )
        pass

    if row.coursework_mark_fraction + row.exam_mark_fraction > 1:
        logger.warning(
            f"Row {idx+2}: {row.code} - {row.name}: Mark fraction total is {row.coursework_mark_fraction + row.exam_mark_fraction}"
        )

    else:
        academic_group: AcademicGroup|None = None
        if "laser" in str(row.name).lower():
            academic_group = AcademicGroup.objects.get(code='Q')
        elif "astro" in str(row.name).lower():
            academic_group = AcademicGroup.objects.get(code='A')
        elif "particle" in str(row.name).lower():
            academic_group = AcademicGroup.objects.get(code='T')
        else:
            academic_group = None

        unit, created = Unit.objects.get_or_create(
            code=code,
            name=row.unit_name,
            description=row.unit_name,
            students=row.students if not isnull(row.students) else None,
            synoptic_lectures=row.synoptic_lectures if not isnull(row.synoptic_lectures) else None,
            lectures=row.lectures if not isnull(row.lectures) else None,
            coursework=row.coursework if not isnull(row.coursework) else None,
            coursework_mark_fraction=row.coursework_mark_fraction if not isnull(row.coursework_mark_fraction) else None,
            exams=1 if not isnull(row.exam_mark_fraction) else 0,
            exam_mark_fraction=row.exam_mark_fraction if not isnull(row.exam_mark_fraction) else None,
            credits=row.credits if not isnull(row.credits) else None,
            notes=row.notes if not isnull(row.notes) else "",
            academic_group=academic_group,
        )
        if created:
            unit._history_date = history_date
            unit.save()
            units_created += 1

        task, created = Task.objects.get_or_create(
            unit=unit,
            name="Unit Lead",
            description="Co-ordinates/teaches unit.",
            is_lead=True,
            is_required=True,
            is_unique=True,
            coursework_fraction=row.task__coursework_fraction if not isnull(row.task__coursework_fraction) else 0,
            exam_fraction=row.task__exam_fraction if not isnull(row.task__exam_fraction) else 0,
        )
        if created:
            task._history_date = history_date
            task.save()
            tasks_created += 1

        if row.hours_fixed_deputy:
            task, created = Task.objects.get_or_create(
                unit=unit,
                name="Deputy Lead",
                description="Deputy co-ordinator for the unit.",
                is_required=True,
                is_unique=True,
                load_fixed=row.hours_fixed_deputy,
            )
            if created:
                task._history_date = history_date
                task.save()
                tasks_created += 1

# Stop tracking history changes.
settings.SIMPLE_HISTORY_ENABLED = False

logger.info(
    f"Import complete. Created {units_created} units, {tasks_created} tasks"
)
