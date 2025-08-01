"""
Imports the Staff Contract Detail tab of the spreadsheet

Needs to be run within the Django context; open the management shell with:

    ```
    uv run manage.py shell < import_staff_from_csv.py
    ```
"""
from logging import Logger, getLogger
from datetime import datetime
from zoneinfo import ZoneInfo
from os import getcwd
from pathlib import Path
from uuid import uuid4
from typing import Dict

from django.db.models import Sum
from pandas import DataFrame, read_csv, isna
from django.conf import settings
from app.models import Staff, AcademicGroup


logger: Logger = getLogger(__name__)


# Hardcoded for ease of dealing with the manage.py shell.
CSV_PATH: Path = Path(getcwd()) / "spreadsheet_staff_contract_cut.csv"
print(f"Importing staff from: {CSV_PATH}")

# Track the history of creation
settings.SIMPLE_HISTORY_ENABLED = True

# Read the staff CSV, and convert the empty cells to 0.
staff_df: DataFrame = read_csv(CSV_PATH, header=0, index_col=False)
staff_df.info()
staff_df['fte frac'].fillna(0, inplace=True)
staff_df['Fixed hrs '].fillna(0, inplace=True)
staff_df['Cumulative to AY21/22'].fillna(0, inplace=True)
staff_df['Cumulative Overload at end 22/23'].fillna(0, inplace=True)
staff_df['Over/Underload This year'].fillna(0, inplace=True)

date_2022: datetime = datetime(year=2022, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))
date_2023: datetime = datetime(year=2023, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))
date_2024: datetime = datetime(year=2024, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))

for idx, row in staff_df.iterrows():
    # Iterate through the dataframe, and for each row create a new staff member and save their details.
    print(f"Importing staff {idx}: {row['STAFF']}")
    if not isna(row['Group']):
        group: AcademicGroup|None = AcademicGroup.objects.get(code=row['Group'])
    else:
        group = None

    try:
        # Skip if the staff have already been imported
        staff: Staff = Staff.objects.get(name=row['STAFF'])
        logger.info(
            f"Found staff: {staff}: {row['STAFF']}"
        )
        continue
    except Staff.DoesNotExist:
        pass

    staff: Staff = Staff(
        account=f"unconnected-{str(uuid4())[:4]}",
        name=row['STAFF'],
        gender=row['Gender'],
        fte_fraction=row['fte frac'] if not isna(row['fte frac']) else 0,
        hours_fixed=row['Fixed hrs '] if not isna(row['Fixed hrs '])  else 0,
        academic_group=group if group else None,
        notes=row['Comment'] if not isna(row['Comment']) else "",
    )

    # Now, for each historical balance associated with a given year,
    # add it to the model then save timestamped to the 'end of year' date.
    staff._history_date = date_2022
    staff.load_balance_final = row['Cumulative to AY21/22']
    staff.load_balance_historic = 0
    staff.save()

    staff._history_date = date_2023
    staff.load_balance_final = row['Cumulative Overload at end 22/23'] - row['Cumulative to AY21/22']
    staff.load_balance_historic = row['Cumulative Overload at end 22/23']
    staff.save()

    staff._history_date = date_2024
    staff.load_balance_final = row['Over/Underload This year']
    staff.load_balance_historic = row['Cumulative Overload at end 22/23'] + row['Over/Underload This year']
    staff.save()

for academic_group in AcademicGroup.objects.all():
    aggregates: Dict[str, int] = Staff.history.as_of(date_2022).filter(academic_group=academic_group).aggregate(
        Sum('load_balance_final'), Sum('load_balance_historic')
    )
    load_balance_final: int = aggregates['load_balance_final__sum'] if aggregates['load_balance_final__sum'] else 0
    load_balance_historic: int = aggregates['load_balance_historic__sum'] if aggregates['load_balance_historic__sum'] else 0

    academic_group._history_date = date_2022
    academic_group.load_balance_final = load_balance_final
    academic_group.load_balance_historic = load_balance_historic
    academic_group.save()

    aggregates: Dict[str, int] = Staff.history.as_of(date_2023).filter(academic_group=academic_group).aggregate(
        Sum('load_balance_final')
    )
    load_balance_final: int = aggregates['load_balance_final__sum'] if aggregates['load_balance_final__sum'] else 0
    load_balance_historic += load_balance_final

    academic_group._history_date = date_2023
    academic_group.load_balance_final = load_balance_final
    academic_group.load_balance_historic = load_balance_historic
    academic_group.save()

    aggregates: Dict[str, int] = Staff.history.as_of(date_2024).filter(academic_group=academic_group).aggregate(
        Sum('load_balance_final')
    )
    load_balance_final: int = aggregates['load_balance_final__sum'] if aggregates['load_balance_final__sum'] else 0
    load_balance_historic += load_balance_final

    academic_group._history_date = date_2024
    academic_group.load_balance_final = load_balance_final
    academic_group.load_balance_historic = load_balance_historic
    academic_group.save()

# Stop tracking history changes.
settings.SIMPLE_HISTORY_ENABLED = False
