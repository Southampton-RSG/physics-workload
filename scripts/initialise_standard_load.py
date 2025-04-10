from app.models import StandardLoad

standard_load: StandardLoad = StandardLoad.objects.latest()
standard_load.update_target_load_per_fte()
standard_load.update_calculated_loads()
