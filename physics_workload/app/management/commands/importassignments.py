from argparse import ArgumentParser
from datetime import datetime
from logging import Logger, getLogger
from pathlib import Path
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.management.base import BaseCommand
from pandas import DataFrame, isna, read_excel

from app.management.load_utils import (
    ADMIN_PREFIXES,
    SPECIAL_CODES,
    TITLE_DISSERTATION,
    TITLE_PROJECT_MARKING,
    TITLE_UNIT_DEPUTY,
    TITLE_UNIT_LEAD,
    UNIT_PREFIXES,
    load_staff_tasks_from_excel,
    xlsx_file_only,
)
from app.models import AcademicGroup, Assignment, Staff, Task, Unit

logger: Logger = getLogger(__name__)


class Command(BaseCommand):
    help = "Loads assignments to non-unit tasks from the Staff Tasks tab of the spreadsheet that has been exported to CSV."

    def add_arguments(self, parser: ArgumentParser):
        """
        Adds the positional argument for email, and flag for superuser status.

        :param parser: The argument parser object.
        """
        parser.add_argument(
            "path",
            type=xlsx_file_only,
            help="Path to excel file for units",
        )
        parser.add_argument("year", type=int, help="Starting year of the spreadsheet, i.e. 24 for 2024/2025.")

    def handle(self, *args: Path, **options):
        """
        Imports Units from the Load Master tab of the spreadsheet

        :param args: The list of Excel files (2024/2025, 2025/2026).
        :param options: The dictionary of options passed to the script.
        """

        # Set up logging
        logger: Logger = getLogger(__name__)

        # Track the history of creation
        settings.SIMPLE_HISTORY_ENABLED = True
        history_date: datetime = datetime(
            year=options["year"],
            month=9,
            day=20,
            hour=0,
            minute=0,
            second=0,
            tzinfo=ZoneInfo("GMT"),
        )

        # Read the XLSX
        load_df: DataFrame = load_staff_tasks_from_excel(options["path"])

        # Track what we're creating
        assignments_created: list[Assignment] = []
        assignments_skipped: list[Assignment] = []
        assignments_failed: list[int] = []
        students_failed: list[str] = []

        # Make sure all the staff are valid
        staff_missing: list[str] = []
        for staff__name in load_df.staff__name.unique():
            try:
                staff: Staff = Staff.objects.get(name__iexact=staff__name)
            except Staff.DoesNotExist:
                staff_missing.append(staff__name)
                logger.error(f"Staff '{staff__name}' does not exist.")

        if staff_missing:
            staff_missing.sort()
            self.stderr.write(self.style.WARNING(f"Staff not imported: {', '.join(staff_missing)}"))

        # Make sure all the units are valid
        units_missing: list[str] = []
        for unit__code in set(load_df.unit__code.astype("str").unique()) - ADMIN_PREFIXES - SPECIAL_CODES:
            try:
                unit: Unit = Unit.objects.get(code=unit__code)
            except Unit.DoesNotExist:
                units_missing.append(unit__code)
                logger.error(f"Unit '{unit__code}' does not exist.")

        if units_missing:
            units_missing.sort()
            self.stderr.write(self.style.WARNING(f"Units not imported: {', '.join(units_missing)}"))

        tasks_missing: list[str] = []
        for idx, row in load_df.iterrows():
            academic_group: AcademicGroup | None = None
            students: list[int] | None = None
            task: Task | None = None
            staff: Staff | None = None
            unit: Unit | None = None
            title: str | None = None

            # Iterate through the dataframe, and for each row create a new unit and save the details.
            try:
                staff = Staff.objects.get(name__iexact=row.staff__name)
            except Staff.DoesNotExist:
                assignments_failed.append(idx)
                continue

            try:
                # Look for an academic group if possible
                academic_group = AcademicGroup.objects.get(code=str(row.academic_group__name)[0])
            except AcademicGroup.DoesNotExist:
                pass  # Some tasks don't need one anyway

            if row.unit__code in units_missing:
                assignments_failed.append(idx)
                continue

            elif row.unit__code.upper() in ADMIN_PREFIXES:
                # Found an admin task
                logger.debug(f"Importing admin task from row {idx}")

                try:
                    task: Task = Task.objects.get(
                        title__iexact=row.task__title,
                        academic_group=academic_group,
                    )
                except Task.DoesNotExist:
                    try:
                        task = Task.objects.get(
                            title__iexact=row.task__title,
                        )
                    except Task.DoesNotExist:
                        logger.error(f"Task '{row.task__title}' does not exist.")
                        tasks_missing.append(row.task__title)
                        assignments_failed.append(idx)
                        continue

            elif row.unit__code[:4].upper() in UNIT_PREFIXES:
                # Found a unit task
                logger.debug(f"Importing unit task from row {idx}")

                try:
                    unit = Unit.objects.get(code=row.unit__code)
                except Unit.DoesNotExist:
                    pass

                if isinstance(row.task__title, str):
                    if "coord" in row.task__title.lower():
                        title = TITLE_UNIT_LEAD
                    elif "deputy" in row.task__title.lower():
                        title = TITLE_UNIT_DEPUTY

                if not title and isinstance(row.task__description, str):
                    if "project" in row.task__description.lower():
                        title = TITLE_PROJECT_MARKING
                    elif "dissertation" in row.task__description.lower():
                        title = TITLE_DISSERTATION

                    if "+" in str(row.task__title):
                        assignments_failed.append(idx)
                        students_failed.append(row.task__title)
                        continue

                    students = []
                    for value in str(row.task__title).split():
                        try:
                            students.append(int(value))
                        except ValueError:
                            pass

                if not title:
                    title = row.task__description.lower()

                try:
                    task: Task = Task.objects.get(
                        unit=unit,
                        title__iexact=title,
                    )
                except Task.DoesNotExist:
                    logger.error(f"Task '{unit} - {row.task__title}' does not exist.")
                    tasks_missing.append(f"{unit} - {row.task__title}")
                    assignments_failed.append(idx)
                    continue

            elif row.unit__code.upper() in SPECIAL_CODES:
                if row.unit__code.upper() == "TUTOR":
                    if not isna(row.task__notes) and "S1" in row.task__notes:
                        task = Task.objects.get(title__iexact="Drop-In Sessions (S1)")
                    elif not isna(row.task__notes) and "S2" in row.task__notes:
                        task = Task.objects.get(title__iexact="Drop-In Sessions (S2)")
                    else:
                        task = Task.objects.get(title__iexact="Tuition")
                        students = [row.assignment__students]
                else:
                    assignments_failed.append(idx)
                    continue
            else:
                logger.error(f"Row {idx} - {row.task__title}' does not exist.")
                assignments_failed.append(idx)
                continue

            try:
                assignment: Assignment = Assignment.objects.get(task=task, staff=staff)
                assignments_skipped.append(assignment)
            except Assignment.MultipleObjectsReturned:
                continue

            except Assignment.DoesNotExist:
                if students:
                    for student_number in students:
                        assignment = Assignment(
                            task=task,
                            staff=staff,
                            is_first_time=True,
                            is_provisional=True,
                            students=student_number,
                        )
                        assignment._history_date = history_date
                        assignment.save()
                        assignments_created.append(assignment)
                else:
                    assignment = Assignment(
                        task=task,
                        staff=staff,
                        is_first_time=True,
                        is_provisional=True,
                    )
                    assignment._history_date = history_date
                    assignment.save()
                    assignments_created.append(assignment)

        settings.SIMPLE_HISTORY_ENABLED = False

        if tasks_missing:
            tasks_missing.sort()
            self.stderr.write(self.style.WARNING(f"Tasks not imported: {', '.join(tasks_missing)}"))

        if students_failed:
            students_failed.sort()
            self.stderr.write(self.style.WARNING(f"Student counts not parsed: {', '.join(students_failed)}"))
            self.stderr.write(self.style.WARNING("Just use a spaced list, e.g. '1 2 1'"))

        self.stdout.write(self.style.SUCCESS(f"Assignments complete. Created: {len(assignments_created)}, skipped: {len(assignments_skipped)}."))

        dataframe_failed: DataFrame = read_excel(options["path"], sheet_name="Staff Tasks", header=0, index_col=False).loc[assignments_failed]
        dataframe_failed.to_csv("failed_assignments.csv", index=False)
