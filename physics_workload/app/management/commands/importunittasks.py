from argparse import ArgumentParser
from datetime import datetime
from logging import Logger, getLogger
from pathlib import Path
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.management.base import BaseCommand
from pandas import DataFrame, isnull

from app.management.load_csv import load_staff_tasks_from_excel, xlsx_file_only
from app.models import Assignment, Staff, Task, Unit, LoadFunction

logger: Logger = getLogger(__name__)


class Command(BaseCommand):
    help = "Loads assignments to unit tasks from the Staff Tasks tab of the spreadsheet that has been exported to CSV."

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
        assignments_deleted: int = 0
        assignments_failed: int = 0
        tasks_created: int = 0

        marking_bsc: LoadFunction = LoadFunction.objects.get(name__icontains="bsc")
        marking_msc: LoadFunction = LoadFunction.objects.get(name__icontains="msc")

        for year, load_file in load_files.items():
            # Read the staff CSV, and convert the empty cells to 0.
            load_df: DataFrame = load_staff_tasks_from_excel(load_file)
            load_df.to_csv("unit_tasks.csv")

            history_date: datetime = datetime(year=2024, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))

            for idx, row in load_df.iterrows():
                # Iterate through the dataframe, and for each row create a new unit and save the details.
                code: str = row.code
                task: Task | None = None
                unit: Unit | None = None
                students: int | None = None

                found_assignment: bool = False
                save_assignment: bool = False

                if isnull(code) or not code or (code[:4] != "PHYS" and code[:4] != "OPTO"):
                    # Skip this line if it's not a valid unit code
                    continue
                else:
                    logger.debug(f"\nImporting row {idx}: {row.code}")

                try:
                    # Skip this line if the unit's already been created
                    unit: Unit = Unit.objects.get(code=code)
                    logger.debug(f"Found {code}: {row.task__title}")
                except Unit.DoesNotExist:
                    logger.warning(f"No unit code: {code}")
                    assignments_failed += 1
                    continue

                try:
                    # Skip this if the staff can't be found
                    staff: Staff = Staff.objects.get(name=row.staff__name)
                    logger.debug(f"Found staff: {staff}: {row.staff__name}")
                except Staff.DoesNotExist:
                    logger.warning(f"No staff named: {row.staff__name}")
                    assignments_failed += 1
                    continue

                if str(row.task__title).lower() == "coord":
                    try:
                        task = Task.objects.get(unit=unit, is_lead=True)
                        logger.debug(f"Found existing lead task: {task}")
                    except Task.DoesNotExist:
                        logger.warning("No lead task named: {task}")
                        assignments_failed += 1
                        continue

                elif str(row.task__title).lower() == "deputy":
                    try:
                        task = Task.objects.get(unit=unit, title="Deputy Lead")
                        logger.debug(f"Found existing deputy lead task: {task}")
                    except Task.DoesNotExist:
                        logger.warning("No deputy task named: {task}")
                        assignments_failed += 1
                        continue

                elif str(row.task__description).lower().contains("projects marked"):
                    # We just create the task as the format for recording them is inconsistent
                    try:
                        task = Task.objects.get(unit=unit, title__icontains="marking")
                    except Task.DoesNotExist:
                        task = Task(
                            unit=unit,
                            title="Project Marking",
                            load_function=marking_bsc if row.task__title.lower().contains("bsc") else marking_msc,
                        )
                        tasks_created += 1
                        continue
                else:
                    continue

                assignment: Assignment | None = None
                try:
                    if task.is_unique:
                        assignment = Assignment.objects.get(task=task)
                    else:
                        assignment = Assignment.objects.get(task=task, staff=staff)
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
                        is_first_time=False,
                        is_provisional=True,
                    )
                    save_assignment = True

                if save_assignment:
                    try:
                        assignment._history_date = history_date
                        assignment.save()
                    except Exception as e:
                        logger.exception(e)
                        raise e

            # Delete any assignments that haven't been updated
            for assignment in Assignment.objects.all():
                if assignment.history.order_by('-history_date').first().history_date.year != year:
                    assignment.delete()
                    assignments_deleted += 1

        # Stop tracking history changes.
        settings.SIMPLE_HISTORY_ENABLED = False

        self.stdout.write(
            self.style.SUCCESS(
                f"Unit task assignments complete. Created: {assignments_created}, updated: {assignments_updated}, skipped: {assignments_skipped}, deleted: {assignments_deleted}, failed: {assignments_failed}.\n"
                f"New tasks created: {tasks_created}."
            )
        )
