from datetime import datetime

from django.http import HttpRequest

from app.models import AcademicGroup, Assignment, Staff, StandardLoad, Task


def year_to_academic_year(date: datetime) -> str:
    """
    Output function for producing tidy dates.

    :param date: A datetime for the last year of an academic year (e.g. 2024/06/15)
    :return: The academic year that datetime belongs to (e.g. 23/24)
    """
    return f"{str(date.year - 1)[-2:]}/{str(date.year)[-2:]}"


def update_all_loads(request: HttpRequest | None = None) -> int:
    """
    Updates the load of all assignments, staff, e.t.c.

    A very expensive function but required given the weirdly self-referential definition.

    :param request: The web request, required to provide an output message.
    :return: The number of cycles taken to update the full-time equivalent loads.
    """
    standard_load: StandardLoad = StandardLoad.objects.latest()

    # We don't use this but let's ignore the warning for now
    target_load_start: int = standard_load.target_load_per_fte_calc  # noqa: F841

    for task in Task.objects.all():
        task.update_load()

    for assignment in Assignment.objects.all():
        assignment.update_load()

    for staff in Staff.objects.all():
        staff.update_load_assigned()

    cycles: int = 0
    calculating_full_time: bool = True

    while calculating_full_time:
        # We need to repeat this until the 'Full time task' load stops changing...
        calculating_full_time = False
        cycles += 1

        # Recalculate what a 'full time' load actually is
        standard_load.update_target_load_per_fte()

        # Then, for tasks using a full-time load...
        for task in Task.objects.filter(is_full_time=True).all():
            if task.update_load():
                calculating_full_time = True
                for assignment in task.assignment_set.all():
                    assignment.staff.update_load_assigned()

    # Now we've finally settled on what 'full time' actually is, update all the staff with that
    for staff in Staff.objects.all():
        staff.update_load_target()

    for academic_group in AcademicGroup.objects.all():
        academic_group.update_load()

    # We don't use this but let's ignore the warning for now
    target_load_finish: int = standard_load.target_load_per_fte_calc  # noqa: F841

    return cycles
