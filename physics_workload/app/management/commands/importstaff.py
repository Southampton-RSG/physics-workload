from argparse import ArgumentParser, FileType
from datetime import datetime
from logging import Logger, getLogger
from pathlib import Path
from typing import Dict
from uuid import uuid4
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Sum
from pandas import DataFrame, isna, read_csv

from app.management.load_utils import csv_file_only, load_staff_contracts_from_excel, xlsx_file_only
from app.models import AcademicGroup, Staff

logger: Logger = getLogger(__name__)


class Command(BaseCommand):
    help = "Loads the 2024-2025 and 2025-2026 spreadsheets' Staff Contract Hours tabs that have been exported to CSV."

    def add_arguments(self, parser: ArgumentParser):
        """
        Adds the positional argument for email, and flag for superuser status.

        :param parser: The argument parser object.
        """
        parser.add_argument(
            "2024",
            type=xlsx_file_only,
            help="Excel file for 2024/2025",
        )
        parser.add_argument(
            "2025",
            type=xlsx_file_only,
            help="Excel file for 2025/2026",
        )

    def handle(self, *args: Path, **options):
        """
        Imports the Staff Contract Detail tab of the spreadsheet

        :param args:
        :param options:
        :return:
        """

        # Track the history of creation
        settings.SIMPLE_HISTORY_ENABLED = True

        staff24_path: Path = options["2024"]
        staff25_path: Path = options["2025"]

        # Track how many we're creating
        staff_created: int = 0
        staff_skipped: int = 0
        staff_updated: int = 0

        # Read the staff CSV, and convert the empty cells to 0.
        staff24_df: DataFrame = load_staff_contracts_from_excel(staff24_path)
        staff25_df: DataFrame = load_staff_contracts_from_excel(staff25_path)

        date_2022: datetime = datetime(year=2022, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))
        date_2023: datetime = datetime(year=2023, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))
        date_2024: datetime = datetime(year=2024, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))
        date_2025: datetime = datetime(year=2025, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))

        for idx, row in staff24_df.iterrows():
            # Iterate through the dataframe, and for each row create a new staff member and save their details.
            logger.debug(f"Importing staff {idx}: {row['name']}")
            if not isna(row["academic_group"]):
                group: AcademicGroup | None = AcademicGroup.objects.get(code=row["academic_group"])
            else:
                group = None

            try:
                # Skip if the staff have already been imported
                staff: Staff = Staff.objects.get(name=row["name"])
                logger.debug(f"Found staff: {staff}: {row['name']}")
                continue
            except Staff.DoesNotExist:
                pass

            staff: Staff = Staff(
                account=f"unconnected-{str(uuid4())[:4]}",
                name=row["name"],
                gender=row["gender"],
                fte_fraction=row["fte_fraction"] if not isna(row["fte_fraction"]) else 0,
                hours_fixed=row["hours_fixed"] if not isna(row["hours_fixed"]) else 0,
                academic_group=group if group else None,
                notes=row["notes"] if not isna(row["notes"]) else "",
            )
            staff_created += 1

            # Now, for each historical balance associated with a given year,
            # add it to the model then save timestamped to the 'end of year' date.
            staff._history_date = date_2022
            staff.load_balance_final = row["Cumulative to AY21/22"]
            staff.load_balance_historic = 0
            staff.save()

            staff._history_date = date_2023
            staff.load_balance_final = row["Cumulative Overload at end 22/23"] - row["Cumulative to AY21/22"]
            staff.load_balance_historic = row["Cumulative Overload at end 22/23"]
            staff.save()

            staff._history_date = date_2024
            staff.load_balance_final = row["load_balance_final"]
            staff.load_balance_historic = row["Cumulative Overload at end 22/23"] + row["load_balance_final"]
            staff.save()

        for idx, row in staff25_df.iterrows():
            # Iterate through the dataframe, and for each row create a new staff member and save their details.
            if not isna(row["academic_group"]):
                group: AcademicGroup | None = AcademicGroup.objects.get(code=row["academic_group"])
            else:
                group = None

            try:
                # If the staff have already been imported...
                staff: Staff = Staff.objects.get(name=row["name"])
                logger.info(f"Found staff: {staff}: {row['name']}")

                if staff.history.order_by('-history_date').first().history_date.year != 2025:
                    # Have we already done 2025?
                    staff_updated += 1
                    staff._history_date = date_2025
                    staff.load_balance_historic = staff.load_balance_historic + staff.load_balance_final
                    staff.load_balance_final = row["load_balance_final"]
                    staff.save()
                else:
                    staff_skipped += 1

            except Staff.DoesNotExist:
                staff: Staff = Staff(
                    account=f"unconnected-{str(uuid4())[:4]}",
                    name=row["name"],
                    gender=row["gender"],
                    fte_fraction=row["fte_fraction"] if not isna(row["fte_fraction"]) else 0,
                    hours_fixed=row["hours_fixed"] if not isna(row["hours_fixed"]) else 0,
                    academic_group=group if group else None,
                    notes=row["notes"] if not isna(row["notes"]) else "",
                )
                staff_created += 1

                staff._history_date = date_2025
                staff.load_balance_historic = 0
                staff.load_balance_final = row["load_balance_final"]
                staff.save()

        # Stop tracking history changes.
        settings.SIMPLE_HISTORY_ENABLED = False

        self.stdout.write(
            self.style.SUCCESS(f"Staff complete. Created: {staff_created}, updated: {staff_updated}, skipped: {staff_skipped}.")
        )

