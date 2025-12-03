from argparse import ArgumentParser
from datetime import datetime
from logging import Logger, getLogger
from pathlib import Path
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.management.base import BaseCommand
from pandas import DataFrame, isnull, isna

from app.management.load_utils import load_staff_tasks_from_excel, xlsx_file_only, load_nonunit_tasks_from_excel
from app.models import AcademicGroup, Task

logger: Logger = getLogger(__name__)


class Command(BaseCommand):
    help = "Loads non-unit tasks from the Load Master tab of the spreadsheet."

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
        parser.add_argument(
            "year",
            type=int,
            help="Starting year of the spreadsheet, i.e. 24 for 2024/2025."
        )

    def handle(self, *args: Path, **options):
        """
        Imports non-unit tasks from the Load Master tab of the spreadsheet

        :param args: The list of CSV files (2024/2025, 2025/2026).
        :param options: The dictionary of options passed to the script.
        """

        # Set up logging
        logger: Logger = getLogger(__name__)

        # Read the XLSX
        load_df: DataFrame = load_nonunit_tasks_from_excel(options["path"])

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

        # Track what we're creating
        tasks_created: list[Task] = []
        tasks_skipped: list[Task] = []

        for idx, row in load_df.iterrows():
            # Senior Tutor roles are fixtures
            if "senior tutor" in row.task__title.lower():
                continue

            # Iterate through the dataframe, and for each row create a new task and save the details.
            try:
                task: Task = Task.objects.get(
                    academic_group=AcademicGroup.objects.get(code=row.academic_group__short_name[0]) if not isnull(row.academic_group__short_name) else None,
                    title=row.task__title
                )
                tasks_skipped.append(task)
                logger.debug(f"Skipping task: {task}")
                continue

            except Task.DoesNotExist:
                task = Task(
                    academic_group=AcademicGroup.objects.get(code=row.academic_group__short_name[0])
                    if not isnull(row.academic_group__short_name)
                    else None,
                    title=row.task__title,
                    description=row.task__description,
                    notes=row.task__notes,
                    load_fixed=row.task__load_fixed if row.task__load_fixed != -1 else 0,
                    load_fixed_first=row.task__load_fixed_first if row.task__load_fixed != -1 and not isna(row.task__load_fixed_first) else None,
                    is_full_time=(row.task__load_fixed == -1),
                )
                tasks_created.append(task)
                task._history_date = history_date
                logger.info(f"Creating new task: {task}")

                try:
                    logger.info(f"Saving task: {task}")
                    task.save()
                except Exception as e:
                    logger.error(f"Failed to save task from: {row}")
                    logger.exception(e)
                    raise e

            except Exception as e:
                logger.exception(f"Failed to load task: {row.task__title}")
                raise e

        settings.SIMPLE_HISTORY_ENABLED = False
        self.stdout.write(
            self.style.SUCCESS(f"Non-unit tasks complete. Created: {len(tasks_created)}, skipped: {len(tasks_skipped)}")
        )
