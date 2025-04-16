"""
Imports the Staff Contract Detail tab of the spreadsheet

Needs to be run within the Django context; open the management shell with:

    ```
    uv run manage.py shell
    ```

Then execute this file with:

    ```
    exec(open("/home/toaster/physics-workload/scripts/import_staff_from_csv.py").read())
    ```

Annoyingly, because of this the path has to be hardcoded.
"""
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from simpleeval import simple_eval
import pandas
from pandas import DataFrame, read_csv, isna, isnull, to_numeric
from pandas.api.types import is_numeric_dtype
from django.conf import settings
from app.models import Unit


# Hardcoded for ease of dealing with the manage.py shell.
CSV_PATH: str = Path("~/projects/physics-workload/spreadsheet_load_master.csv")
print(f"Importing units from: {CSV_PATH}")

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
        'Fraction of Courseowork marked by coordinator': 'task__coursework_fraction',
        'Examination (fraction of module mark)': 'exam_mark_fraction',
        'Fraction of Examination marked by coordinator': 'task__exam_fraction',
        'Total Number of CATS': 'credits',
        'Task Description': 'task__name',
        'Number of Students': 'students',
        'Description/Unit title': 'name',
        'Task Category/Unit Code': 'code',
        load_df.columns[17]: 'notes'
    },
    inplace=True
)

print("Strip trailing whitespace")
for column in load_df.columns:
    if load_df[column].dtype == 'object':
        load_df[column] = load_df[column].str.strip()

    load_df[load_df[column] == ''] = None

print("Convert raw numbers columns to ints")
for column in [
    'hours_fixed_deputy', 'synoptic_lectures', 'coursework', 'credits', 'students', 'lectures'
]:
    load_df[column] = to_numeric(load_df[column], errors='coerce')
    load_df[column] = load_df[column].fillna(0)

print("Convert fraction columns to floats")
for column in [
    'exam_mark_fraction', 'coursework_mark_fraction',
    'task__coursework_fraction', 'task__exam_fraction',
]:
    equation_rows = load_df[column].str.contains('=').fillna(False)
    load_df[column][equation_rows] = load_df[column][equation_rows].str.lstrip('=').apply(pandas.eval)
    percentage_rows = load_df[column].str.contains('%').fillna(False)
    load_df[column][percentage_rows] = load_df[column][percentage_rows].str.rstrip('%').astype('float')/100.0


for idx, row in load_df.iterrows():
    # Iterate through the dataframe, and for each row create a new staff member and save their details.
    print(f"\nImporting row {idx}: {row.code}")
    print(row)
    code: str = row.code

    if not code or (code[:4] != "PHYS" and code[:4] != "OPTO"):
        # Skip this line if it's not a valid unit code
        continue

    try:
        # Skip this line if the unit's already been created
        unit: Unit = Unit.objects.get(code=code)
        print(
            f"Already found {code}: {row.name}"
        )
        continue

    except Unit.DoesNotExist:
        print(
            f"Creating new unit: {code}"
        )
        pass

    if row.coursework_mark_fraction + row.exam_mark_fraction > 1:
        raise ValueError(
            f"{idx+2} - {row.code} - {row.name}: Mark fraction total is {row.coursework_mark_fraction + row.exam_mark_fraction}"
        )

    unit: Unit = Unit(
        code=code,
        name=row.name,
        description=row.name,
        students=row.students if not isnull(row.students) else None,
        synoptic_lectures=row.synoptic_lectures if not isnull(row.synoptic_lectures) else None,
        lectures=row.lectures if not isnull(row.lectures) else None,
        coursework=row.coursework if not isnull(row.coursework) else None,
        coursework_mark_fraction=row.coursework_mark_fraction if not isnull(row.coursework_mark_fraction) else None,
        exams=1 if not isnull(row.exam_mark_fraction) else 0,
        exam_mark_fraction=row.exam_mark_fraction if not isnull(row.exam_mark_fraction) else None,
        credits=row.credits if not isnull(row.credits) else None,
        notes=row.notes,
    )
    unit._history_date = datetime(year=2024, month=9, day=20, hour=0, minute=0, second=0)
    unit.save()


# Stop tracking history changes.
settings.SIMPLE_HISTORY_ENABLED = False
