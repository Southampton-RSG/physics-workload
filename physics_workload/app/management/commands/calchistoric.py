from datetime import datetime
from logging import Logger, getLogger
from pathlib import Path
from typing import Dict
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Sum
from app.models import AcademicGroup, Staff

logger: Logger = getLogger(__name__)


class Command(BaseCommand):
    help = "Calculates the historic load levels of academic groups in the DB."

    def handle(self, *args: Path, **options):
        """
        Updates the DB to calculate the historic workloads of academic groups from their staff.

        :param args:
        :param options:
        """

        # Track the history of creation
        settings.SIMPLE_HISTORY_ENABLED = True

        date_2022: datetime = datetime(year=2022, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))
        date_2023: datetime = datetime(year=2023, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))
        date_2024: datetime = datetime(year=2024, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))
        date_2025: datetime = datetime(year=2025, month=9, day=20, hour=0, minute=0, second=0, tzinfo=ZoneInfo("GMT"))

        for academic_group in AcademicGroup.objects.all():
            for history in academic_group.history.all():
                history.delete()

            aggregates: Dict[str, int] = (
                Staff.history.as_of(date_2022)
                .filter(academic_group=academic_group)
                .aggregate(Sum("load_balance_final"), Sum("load_balance_historic"))
            )
            load_balance_historic: int = aggregates["load_balance_historic__sum"] if aggregates["load_balance_historic__sum"] else 0
            load_balance_final: int = aggregates["load_balance_final__sum"] if aggregates["load_balance_final__sum"] else 0

            academic_group._history_date = date_2022
            academic_group.load_balance_historic = load_balance_historic
            academic_group.load_balance_final = load_balance_final
            academic_group.save()

            aggregates: Dict[str, int] = Staff.history.as_of(date_2023).filter(academic_group=academic_group).aggregate(Sum("load_balance_final"))
            load_balance_historic += load_balance_final
            load_balance_final: int = aggregates["load_balance_final__sum"] if aggregates["load_balance_final__sum"] else 0

            academic_group._history_date = date_2023
            academic_group.load_balance_historic = load_balance_historic
            academic_group.load_balance_final = load_balance_final
            academic_group.save()

            aggregates: Dict[str, int] = Staff.history.as_of(date_2024).filter(academic_group=academic_group).aggregate(Sum("load_balance_final"))
            load_balance_historic += load_balance_final
            load_balance_final: int = aggregates["load_balance_final__sum"] if aggregates["load_balance_final__sum"] else 0

            academic_group._history_date = date_2024
            academic_group.load_balance_historic = load_balance_historic
            academic_group.load_balance_final = load_balance_final
            academic_group.save()

        # Stop tracking history changes.
        settings.SIMPLE_HISTORY_ENABLED = False

        self.stdout.write(
            self.style.SUCCESS("Calculation finished.")
        )
