# -*- encoding: utf-8 -*-
from typing import Optional, Union, List
from django.db.models import Model, CharField, BooleanField, TextField, ForeignKey, Index
from django.db.models.deletion import PROTECT
from django.db.models.manager import Manager, QuerySet
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from model_utils.managers import QueryManager

from app.models.academic_group import AcademicGroup


class Module(Model):
    """

    """
    code = CharField(max_length=16, blank=False, unique=True)
    name = CharField(max_length=128, blank=False, unique=True)
    academic_group = ForeignKey(
        AcademicGroup, blank=True, null=True, on_delete=PROTECT,
        verbose_name='Group', help_text="The group, if any, responsible for this module",
    )

    has_dissertation = BooleanField(default=False)
    has_placement = BooleanField(default=False)
    is_active = BooleanField(default=True)

    description = TextField(blank=True)

    objects_active = QueryManager(is_active=True)
    objects = Manager()

    class Meta:
        indexes = [
            Index(fields=['code']),
        ]
        ordering = ['name']
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

    def get_absolute_url(self) -> str:
        return reverse_lazy('module_detail', args=[self.code])

    def get_latest_year(self) -> Optional['ModuleYear']:
        """
        :return: Returns the most recent occurrence of this module, or None if there isn't one.
        """
        try:
            return self.module_years.latest()
        except ObjectDoesNotExist:
            return None

    def get_latest_year_queryset(self) -> Union[QuerySet, List['ModuleYear']]:
        """
        :return: Returns the most recent occurrence of this module as a list (for feeding to Tables) or an empty queryset if not.
        """
        try:
            return [self.module_years.latest()]
        except ObjectDoesNotExist:
            return self.module_years.none()
