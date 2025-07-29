from django.core.management.base import BaseCommand  # , CommandError

from app.utility import update_all_loads


class Command(BaseCommand):
    help = "Initialises the loads of all models in the database."

    def handle(self, *args, **options):
        """

        :param args:
        :param options:
        :return:
        """
        cycles: int = update_all_loads()
        self.stdout.write(
            self.style.SUCCESS(f"Successfully initialised the loads of all models in the database. Full-time loads took {cycles} cycles.")
        )
