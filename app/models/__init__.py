# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.db.models import Model

from django.db import models
from django.contrib.auth.models import User

from app.models.standard_load import StandardLoad
from app.models.unit import Unit

from app.models.load_function import LoadFunction
from app.models.academic_group import AcademicGroup
from app.models.task import Task
from app.models.assignment import Assignment
from app.models.staff import Staff


class Transaction(models.Model):
    bill_for = models.CharField(max_length=100)
    issue_date = models.DateField()
    due_date = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=10)

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'transaction'
        verbose_name_plural = 'transactions'

    @property
    def status_info(self):
        res = {'class': None}

        if self.status == "Paid":
            res['class'] = 'text-success'
        elif self.status == "Due":
            res['class'] = 'text-warning'
        elif self.status == "Canceled":
            res['class'] = 'text-danger'

        return res
