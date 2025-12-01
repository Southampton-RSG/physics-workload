from argparse import ArgumentParser, FileType
from datetime import datetime
from logging import Logger, getLogger
from pathlib import Path
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.management.base import BaseCommand
import sqlite3
from pandas import DataFrame, isnull, read_csv

from app.management.load_csv import (
    convert_columns_to_ints,
    convert_percentage_columns_to_floats,
    strip_dataframe_whitespace,
    csv_file_only,
    xlsx_file_only,
    load_units_from_load_master_excel,
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
            help="Path to exdcel file for units",
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
        year: int = options['year']
        history_date: datetime = datetime(year=year, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))

        # Track what's made
        units_created: int = 0
        units_updated: int = 0
        tasks_created: int = 0
        tasks_updated: int = 0

        for idx, row in load_df.iterrows():
            # Iterate through the dataframe, and for each row create a new unit and save the details.
            code: str = row.code
            found_unit: bool = False
            save_unit: bool = False

            if isnull(code) or not code or (code[:4] != "PHYS" and code[:4] != "OPTO"):
                # Skip this line if it's not a valid unit code
                continue
            else:
                logger.debug(f"\nImporting row {idx}: {row.code}")

            try:
                # Skip this line if the unit's already been created
                unit: Unit = Unit.objects.get(code=code)
                found_unit = True
            except Unit.DoesNotExist:
                found_unit = False
            except Exception as e:
                logger.exception(e)
                raise e

            if found_unit:
                if unit.history.order_by('-history_date').first().history_date.year < history_date.year:
                    logger.info(f"Already found {code}: {row.name}, updated to {year}")
                    units_updated += 1
                    unit.students=row.students if not isnull(row.students) else None
                    unit.synoptic_lectures=row.synoptic_lectures if not isnull(row.synoptic_lectures) else None
                    unit.lectures=row.lectures if not isnull(row.lectures) else None
                    unit.coursework=row.coursework if not isnull(row.coursework) else None
                    unit.coursework_mark_fraction=row.coursework_mark_fraction if not isnull(row.coursework_mark_fraction) else None
                    unit.exams=1 if not isnull(row.exam_mark_fraction) else 0
                    unit.exam_mark_fraction=row.exam_mark_fraction if not isnull(row.exam_mark_fraction) else None
                    unit.credits=row.credits if not isnull(row.credits) else None
                    save_unit = True

                else:
                    logger.info(f"Already found {code}: {row.name}")

            else:
                logger.info(f"Creating new unit: {code} - {row.unit_name}")

                if row.coursework_mark_fraction + row.exam_mark_fraction > 1:
                    logger.warning(
                        f"Row {idx + 2}: {row.code} - {row.name}: Mark fraction total is {row.coursework_mark_fraction + row.exam_mark_fraction}"
                    )

                else:
                    if "laser" in str(row.name).lower():
                        academic_group: AcademicGroup | None = AcademicGroup.objects.get(code="Q")
                    elif "astro" in str(row.name).lower():
                        academic_group = AcademicGroup.objects.get(code="A")
                    elif "particle" in str(row.name).lower():
                        academic_group = AcademicGroup.objects.get(code="T")
                    else:
                        academic_group = None

                    units_created += 1
                    unit: Unit = Unit(
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
                    save_unit = True

            if save_unit:
                try:
                    unit._history_date = history_date
                    unit.save()
                except Exception as e:
                    logger.error(f"Failed to save: {row}")
                    logger.exception(f"{e}")
                    raise e

            found_task: bool = False
            save_task: bool = False

            try:
                # Now check for unit lead
                task: Task = Task.objects.get(unit=unit, title="Unit Lead")
                found_task = True
            except Task.DoesNotExist:
                found_task = False
            except Exception as e:
                logger.exception(e)
                raise e

            if found_task:
                if task.history.order_by('-history_date').first().history_date.year < history_date.year:
                    logger.info(f"Already found {task}: Updated to {year}")
                    tasks_updated += 1
                    task.coursework_fraction = row.task__coursework_fraction if not isnull(row.task__coursework_fraction) else 0
                    task.exam_fraction = row.task__exam_fraction if not isnull(row.task__exam_fraction) else 0
                    save_task = True
                else:
                    logger.info(f"Already found {task}")

            else:
                task: Task = Task(
                    unit=unit,
                    title="Unit Lead",
                    description="Co-ordinates/teaches unit.",
                    is_lead=True,
                    is_required=True,
                    is_unique=True,
                    coursework_fraction=row.task__coursework_fraction if not isnull(row.task__coursework_fraction) else 0,
                    exam_fraction=row.task__exam_fraction if not isnull(row.task__exam_fraction) else 0,
                )
                save_task = True
                tasks_created += 1

            if save_task:
                try:
                    task._history_date = history_date
                    task.save()
                except Exception as e:
                    logger.error(f"Failed to save: {row}")
                    logger.exception(f"{e}")
                    raise e

            if row.hours_fixed_deputy:
                found_task = False
                save_task = False

                try:
                    task: Task = Task.objects.get(unit=unit, title="Deputy Lead")
                    found_task = True
                except Task.DoesNotExist:
                    found_task = False
                except Exception as e:
                    logger.exception(e)
                    raise e

                if found_task:
                    if task.history.order_by('-history_date').first().history_date.year < history_date.year:
                        logger.info(f"Already found {task}: Updated to {year}")
                        tasks_updated += 1
                        task.coursework_fraction = row.task__coursework_fraction if not isnull(row.task__coursework_fraction) else 0
                        task.exam_fraction = row.task__exam_fraction if not isnull(row.task__exam_fraction) else 0
                        save_task = True
                    else:
                        logger.info(f"Already found {task}")

                else:
                    task = Task(
                        unit=unit,
                        title="Deputy Lead",
                        description="Deputy co-ordinator for the unit.",
                        is_required=True,
                        is_unique=True,
                        load_fixed=row.hours_fixed_deputy,
                    )
                    save_task = True
                    tasks_created += 1

                if save_task:
                    try:
                        task._history_date = history_date
                        task.save()
                    except Exception as e:
                        logger.error(f"Failed to save: {row}")
                        logger.exception(f"{e}")
                        raise e

        # Stop tracking history changes.
        settings.SIMPLE_HISTORY_ENABLED = False

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete. Created {units_created} units, {tasks_created} tasks. "
                f"Updated {units_updated} units, {tasks_updated} tasks."
            )
        )
