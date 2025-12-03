from argparse import ArgumentParser
from datetime import datetime
from logging import Logger, getLogger
from pathlib import Path
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.management.base import BaseCommand
from pandas import isnull

from app.management.load_utils import (

    xlsx_file_only,
    load_units_from_load_master_excel,
    TITLE_UNIT_LEAD,
    TITLE_UNIT_DEPUTY,
)
from app.models import AcademicGroup, Task, Unit

logger: Logger = getLogger(__name__)


class Command(BaseCommand):
    help = "Loads the units from the Load Master tab of the spreadsheet that has been exported to CSV."

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

    def handle(self, *args, **options):
        """
        Imports Units from the Load Master tab of the spreadsheet

        :param args: The list of arguments.
        :param options: A dict of the arguments with names, and any options.
        """

        load_path: Path = options['path']
        load_df = load_units_from_load_master_excel(load_path)

        # Assign 'fake' dates to when things are being created.
        settings.SIMPLE_HISTORY_ENABLED = True
        history_date: datetime = datetime(year=options["year"], month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))

        # Track what's made
        units_created: list[Unit] = []
        units_skipped: list[Unit] = []
        units_failed: list[int] = []

        tasks_created: list[Task] = []
        tasks_skipped: list[Task] = []

        for idx, row in load_df.iterrows():
            # Iterate through the dataframe, and for each row create a new unit and save the details.
            try:
                # Skip this line if the unit's already been created
                unit: Unit = Unit.objects.get(code=row.code)
                units_skipped.append(unit)
                logger.debug(f"Already imported unit {row.code}")

            except Unit.DoesNotExist:
                # --------------------------------
                # Create the missing unit
                # --------------------------------
                logger.info(f"Creating new unit: {row.code} - {row.unit_name}")

                if row.coursework_mark_fraction + row.exam_mark_fraction > 1:
                    logger.warning(
                        f"Row {idx + 2}: {row.code} - {row.name}: Mark fraction total is {row.coursework_mark_fraction + row.exam_mark_fraction}"
                    )
                    units_failed.append(idx)
                    continue

                if "laser" in str(row.name).lower():
                    academic_group: AcademicGroup | None = AcademicGroup.objects.get(code="Q")
                elif "astro" in str(row.name).lower():
                    academic_group = AcademicGroup.objects.get(code="A")
                elif "particle" in str(row.name).lower():
                    academic_group = AcademicGroup.objects.get(code="T")
                else:
                    academic_group = None

                unit: Unit = Unit(
                    code=row.code,
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
                unit._history_date = history_date
                units_created.append(unit)

                try:
                    unit.save()
                except Exception as e:
                    logger.error(f"Failed to save: {row}")
                    logger.exception(f"{e}")
                    raise e

            except Exception as e:
                logger.exception(e)
                raise e

            # --------------------------------
            # Set the title to look up
            # --------------------------------
            if not row.task__title or isnull(row.task__title) or row.task__title.lower() == "co-ordinator":
                # --------------------------------
                # Does that task exist?
                # --------------------------------
                try:
                    # Now check for unit lead
                    task: Task = Task.objects.get(unit=unit, title=TITLE_UNIT_LEAD)
                    tasks_skipped.append(task)
                    logger.info(f"Skipping task {task}")
                    continue

                except Task.DoesNotExist:
                    # --------------------------------
                    # Create the missing task
                    # --------------------------------
                    task: Task = Task(
                        unit=unit,
                        title=TITLE_UNIT_LEAD,
                        description="Co-ordinates/teaches unit.",
                        assignment_students="INVALID",
                        is_lead=True,
                        is_required=True,
                        is_unique=True,
                        coursework_fraction=row.task__coursework_fraction if not isnull(row.task__coursework_fraction) else 0,
                        exam_fraction=row.task__exam_fraction if not isnull(row.task__exam_fraction) else 0,
                    )
                    task._history_date = history_date
                    tasks_created.append(task)

            else:
                try:
                    # Now check for unit lead
                    task: Task = Task.objects.get(unit=unit, title=row.task__title)
                    tasks_skipped.append(task)
                    logger.info(f"Skipping task {task}")
                    continue

                except Task.DoesNotExist:
                    task: Task = Task(
                        unit=unit,
                        title=row.task__title,
                        description="<PLACEHOLDER>",
                        assignment_students="OPTIONAL",
                        is_lead=False,
                        is_required=False,
                        is_unique=False,
                    )
                    task._history_date = history_date
                    tasks_created.append(task)

            try:
                task.save()
            except Exception as e:
                logger.error(f"Failed to save: {row}")
                logger.exception(f"{e}")
                raise e

            # --------------------------------
            # Look for the deputy task
            # --------------------------------
            if row.hours_fixed_deputy:
                try:
                    task: Task = Task.objects.get(unit=unit, title=TITLE_UNIT_DEPUTY)
                    tasks_skipped.append(task)
                    logger.info(f"Skipping task {task}")

                except Task.DoesNotExist:
                    # --------------------------------
                    # Create the missing task
                    # --------------------------------
                    task = Task(
                        unit=unit,
                        title="Deputy Lead",
                        description="Deputy co-ordinator for the unit.",
                        is_required=True,
                        is_unique=False,
                        load_fixed=row.hours_fixed_deputy,
                    )
                    task._history_date = history_date
                    tasks_created.append(task)

                    try:
                        task.save()
                    except Exception as e:
                        logger.error(f"Failed to save: {row}")
                        logger.exception(f"{e}")
                        raise e

                except Exception as e:
                    logger.exception(e)
                    raise e

        # Stop tracking history changes.
        settings.SIMPLE_HISTORY_ENABLED = False

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete. Created {len(units_created)} units, {len(tasks_created)} tasks. "
                f"Skipped {len(units_skipped)} units, {len(tasks_skipped)} tasks."
            )
        )

        if len(units_failed):
            self.stdout.write(
                self.style.WARNING(
                    f"Failed to import units:\n{load_df.loc[units_failed]}"
                )
            )
