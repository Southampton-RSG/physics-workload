from app.models.staff import Staff
from users.models import CustomUser

staff: Staff = Staff.objects.get(account='swm1r18')
user: CustomUser = staff.user
user.is_superuser = True
user.save()
