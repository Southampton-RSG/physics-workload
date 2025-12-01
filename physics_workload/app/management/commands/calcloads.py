from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Initialises the staff workloads in the database.
    """

    help = "Initialises the staff workloads in the database."

    def handle(self, *args, **options):
        from app.utility import update_all_loads

        try:
            update_all_loads()
        except Exception as e:
            raise CommandError("Could not update staff workloads!")


        self.stdout.write(
            self.style.SUCCESS('Successfully initialised staff workloads.')
        )
