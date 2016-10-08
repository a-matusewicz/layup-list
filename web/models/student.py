from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.conf import settings
from web.models import Review, Vote
from lib import constants


class StudentManager(models.Manager):
    VALID_YEARS = set([str(year) for year in range(15, 25)])

    def is_valid_dartmouth_student_email(self, email):
        e = email.split("@")

        if len(e) < 2:
            return False

        dnd_name = e[0]
        domain = e[1]  # will be 'alumni' for alumni emails
        if domain != "dartmouth.edu":
            return False

        dnd_parts = dnd_name.split('.')

        return (
            dnd_parts[-1] in self.VALID_YEARS or dnd_parts[-1].lower() == "ug")


class Student(models.Model):
    objects = StudentManager()

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    confirmation_link = models.CharField(max_length=16, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def send_confirmation_link(self, request):
        full_link = request.build_absolute_uri(
            reverse('confirmation')) + '?link=' + self.confirmation_link
        if not settings.DEBUG:
            send_mail(
                'Your confirmation link',
                'Please navigate to the following confirmation link: ' +
                full_link, constants.SUPPORT_EMAIL,
                [self.user.email], fail_silently=False
            )

    def can_see_recommendations(self):
        return (Vote.objects.num_good_upvotes_for_user(self.user) >=
                constants.REC_UPVOTE_REQ)

    def __unicode__(self):
        return str(self.user)
