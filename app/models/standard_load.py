from django.core.validators import MinValueValidator
from django.db.models import Model, IntegerField, FloatField, TextField
from django.urls import reverse_lazy
from django.conf import settings
from django.db.models import ObjectDoesNotExist
from django.template.loader import render_to_string


class StandardLoad(Model):
    """
    Standard loads for an academic year
    """
    icon = 'weight-hanging'
    url_root = 'standard_load'

    year = IntegerField(
        unique=True,
        validators=[
            MinValueValidator(settings.YEAR_MINIMUM_VALUE),
        ],
        help_text="Initial year, e.g. 2000 for 2000-2001 academic year."
    )

    load_lecture = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per lecture & problems class",
        help_text="$L_{lec}$",
    )
    load_lecture_first = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per lecture & problems class for first-time assignment",
        help_text="$L_{lec}$ applied when co-ordinating a unit for the first time.",
    )

    load_coursework_set = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per item of coursework prepared",
        help_text="$L_{cw, \mathrm{prep}}$",
    )
    load_coursework_credit = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per coursework credit hour",
        help_text="$L_{cw, \mathrm{credit}}$",
    )
    load_coursework_marked = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per (coursework plus coursework credit hour) marked",
        help_text="$L_{cw, \mathrm{mark}}$",
    )

    load_exam_credit = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per exam credit hour",
        help_text="$L_{e, \mathrm{credit}}$",
    )
    load_exam_marked = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per exam marked",
        help_text="$L_{e, \mathrm{mark}}$",
    )
    load_fte_misc = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Staff misc. load per FTE fraction",
        help_text="Basic allowance apart from explicit task loads"
    )
    hours_fte = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Backstop 'hours per FTE' value",
        help_text="Used when calculating target load hours",
    )

    notes = TextField(blank=True)

    class Meta:
        get_latest_by = 'year'
        ordering = ['-year']
        verbose_name='Standard Load'
        verbose_name_plural='Standard Loads'

    def __str__(self) -> str:
        return f"Load {self.year-2000}/{self.year-1999}"

    def get_absolute_url(self) -> str:
        """
        :return: The URL for the detail view of this particular instance of the model
        """
        return reverse_lazy(StandardLoad.url_root+'_detail', args=[self.year])

    def get_instance_header(self) -> str:
        return render_to_string(
            template_name='app/title.html',
            context={
                'icon': self.icon, 'url': self.get_absolute_url(),
                'text': self
            }
        )

    @staticmethod
    def get_model_url() -> str:
        """
        :return: The URL for the view listing all of this model
        """
        return reverse_lazy(StandardLoad.url_root+'_list')

    @staticmethod
    def get_model_header() -> str:
        return render_to_string(
            template_name='app/title.html',
            context={
                'icon': StandardLoad.icon, 'url': StandardLoad.get_model_url(),
                'text': StandardLoad._meta.verbose_name_plural.title()
            }
        )


def get_current_standard_load() -> StandardLoad|None:
    """
    Wrapper to get current load in a way that won't crash during DB initialisation when it doesn't exit yet.
    :return: Gets the current standard load, or None if it's not yet initialised.
    """
    try:
        return StandardLoad.objects.latest()
    except ObjectDoesNotExist:
        return None
