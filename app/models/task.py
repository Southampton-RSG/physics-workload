# -*- encoding: utf-8 -*-
from django.db.models import Model, CharField, BooleanField, TextField, ForeignKey, Manager
from django.db.models.deletion import PROTECT
from django.urls import reverse_lazy
from model_utils.managers import QueryManager

from app.models.module import Module


class Task(Model):
    """

    """
    module = ForeignKey(
        Module, blank=True, null=True, on_delete=PROTECT,
    )

    name = CharField(max_length=128, blank=False)
    description = TextField(blank=False)

    is_active = BooleanField(default=True)
    objects_active = QueryManager(is_active=True)
    objects = Manager()

    def __str__(self):
        if self.module:
            return f"{self.module.code} - {self.name}"
        else:
            return f"{self.name}"

    class Meta:
        ordering = ('is_active', 'module', 'name',)
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def get_absolute_url(self) -> str:
        return reverse_lazy('task_detail', args=[self.pk])
