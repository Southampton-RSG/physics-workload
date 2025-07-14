from django.core.management.base import BaseCommand, CommandError

from app.models.standard_load import StandardLoad


class Command(BaseCommand):
    help = "Initialises the loads of all models in the database."

    def handle(self, *args, **options):
        """

        :param args:
        :param options:
        :return:
        """
        standard_load: StandardLoad = StandardLoad.objects.latest()
        standard_load.update_calculated_loads()
        standard_load.update_target_load_per_fte()
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully initialised the loads of all models in the database."
            )
        )
