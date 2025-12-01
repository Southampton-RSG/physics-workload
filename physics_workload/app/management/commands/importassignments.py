from argparse import ArgumentParser
from datetime import datetime
from logging import Logger, getLogger
from pathlib import Path
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.management.base import BaseCommand
from pandas import DataFrame, isnull

from app.management.load_csv import load_staff_tasks_from_excel, xlsx_file_only
from app.models import Assignment, Staff, Task, Unit, AcademicGroup

logger: Logger = getLogger(__name__)


class Command(BaseCommand):
    help = "Loads assignments to non-unit tasks from the Staff Tasks tab of the spreadsheet that has been exported to CSV."

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
            help="Excel file for 2025/2026"
        )

    def handle(self, *args: Path, **options):
        """
        Imports Units from the Load Master tab of the spreadsheet

        :param args: The list of Excel files (2024/2025, 2025/2026).
        :param options: The dictionary of options passed to the script.
        """

        settings.SIMPLE_HISTORY_ENABLED = True
        load_files: dict[int, Path] = {
            2024: options["2024"],
            2025: options["2025"],
        }

        # Track what's made
        assignments_created: int = 0
        assignments_updated: int = 0
        assignments_skipped: int = 0
        assignments_failed: int = 0

        for year, load_file in load_files.items():
            # Read the staff CSV, and convert the empty cells to 0.
            load_df: DataFrame = load_staff_tasks_from_excel(load_file)
            load_df.to_csv("test_assignments.csv", index=False)

            history_date: datetime = datetime(year=2024, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))

            for idx, row in load_df.iterrows():
                # Iterate through the dataframe, and for each row create a new unit and save the details.
                code: str = row.code
                task: Task | None = None
                academic_group: AcademicGroup | None = None
                found_assignment: bool = False
                save_assignment: bool = False

                if str(code).upper() not in ["MANG", "COMM", "PCAP"]:
                    # Skip this line if it's not a valid non-unit task code
                    continue
                else:
                    logger.debug(f"Importing row {idx}: {row.code}")

                try:
                    # Skip this if the staff can't be found
                    staff: Staff = Staff.objects.get(name=row.staff__name)
                    logger.debug(f"Found staff: {staff}: {row.staff__name}")
                except Staff.DoesNotExist:
                    logger.warning(f"No staff named: {row.staff__name}")
                    continue

                try:
                    # Look for an academic group if possible
                    academic_group = AcademicGroup.objects.get(code=str(row.academic_group__name)[0])
                except AcademicGroup.DoesNotExist:
                    academic_group = None

                try:
                    task= Task.objects.get(
                        title__iexact=row.task__title,
                        academic_group=academic_group,
                    )
                except Task.DoesNotExist:
                    pass

                if not task:
                    try:
                        task: Task = Task.objects.get(title__iexact=row.task__title)
                    except Task.DoesNotExist:
                        pass

                if not task:
                    # Just manually check then...
                    for task_candidate in Task.objects.filter(unit=None).all():
                        if task_candidate.title.replace(" - ", " ") == row.task__title:
                            task = task_candidate
                        elif task_candidate.title.split("(")[0] == row.task__title:
                            task = task_candidate

                if not task:
                    logger.debug(f"Could not find task named: {row.task__title}")
                    assignments_failed += 1
                    continue

                try:
                    if task.is_unique:
                        assignment: Assignment = Assignment.objects.get(task=task)
                    else:
                        assignment: Assignment = Assignment.objects.get(task=task, staff=staff)

                    found_assignment = True
                except Assignment.DoesNotExist:
                    found_assignment = False
                except Exception as e:
                    logger.exception(e)
                    raise e

                if found_assignment:
                    if assignment.history.order_by('-history_date').first().history_date.year != year:
                        assignments_updated += 1
                        assignment.staff = staff
                        assignment.is_provisional = True
                        save_assignment = True
                    else:
                        assignments_skipped += 1
                else:
                    assignments_created += 1
                    assignment: Assignment = Assignment(
                        task=task,
                        staff=staff,
                        is_first_time=True,
                        is_provisional=True,
                    )
                    save_assignment = True
                    logger.debug(f"Assigning: {staff} to {task}")

                if save_assignment:
                    try:
                        assignment._history_date = history_date
                        assignment.save()
                    except Exception as e:
                        logger.exception(e)
                        raise e

        # Stop tracking history changes.
        settings.SIMPLE_HISTORY_ENABLED = False

        self.stdout.write(
            self.style.SUCCESS(f"Non-unit task assignments complete. Created: {assignments_created}, updated: {assignments_updated}, skipped: {assignments_skipped}, failed: {assignments_failed}.")
        )
