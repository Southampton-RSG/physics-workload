"""
There's no way to programmatically create a superuser with a specific password,
except via Python script.
This is obviously insecure and purely for testing.
"""
from django.contrib.auth import get_user_model

superuser = get_user_model().objects.filter(username='teachingtimetool').first()
superuser.set_password("mattmiddleton")
superuser.save()