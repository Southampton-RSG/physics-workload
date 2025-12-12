from django.core.management.base import BaseCommand

from app.models import Task


class Command(BaseCommand):
    """
    Initialises the staff workloads in the database.
    """

    help = "Fixes imported tasks where the 'first time' value is not a bonus added, but the flat value."

    def handle(self, *args, **options):
        fixed_loads: int = 0

        for task in Task.objects.all():
            if task.load_fixed_first and task.load_fixed_first > task.load_fixed:
                task.load_fixed_first = task.load_fixed_first - task.load_fixed
                task.save()
                fixed_loads += 1

            if task.is_lead or task.is_full_time or task.is_unique:
                task.assignment_students = Task.AssignmentStudentsChoices.INVALID

        self.stdout.write(self.style.SUCCESS(f"Successfully fixed {fixed_loads} tasks."))
