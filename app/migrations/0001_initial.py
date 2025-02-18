# Generated by Django 5.1.5 on 2025-02-14 17:56

import django.core.validators
import django.db.models.deletion
import django.db.models.manager
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=1, unique=True)),
                ('name', models.CharField(max_length=128, unique=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Academic Group',
                'verbose_name_plural': 'Academic Groups',
                'ordering': ('name',),
            },
            managers=[
                ('objects_active', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='LoadFunction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('expression', models.TextField(verbose_name='Weighting Expression')),
                ('is_active', models.BooleanField(default=True)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Dissertation Load Function',
                'verbose_name_plural': 'Dissertation Load Functions',
                'ordering': ('name',),
            },
            managers=[
                ('objects_active', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='StandardLoad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(help_text='Initial year, e.g. 2000 for 2000-2001 academic year.', unique=True, validators=[django.core.validators.MinValueValidator(2000)])),
                ('load_lecture', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Load hours per lecture & problems class')),
                ('load_lecture_first', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Load hours per lecture & problems class for first-time assignment')),
                ('load_coursework_set', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Load hours per item of coursework prepared')),
                ('load_coursework_credit', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Load hours per coursework credit hour')),
                ('load_coursework_marked', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Load hours per (coursework plus coursework credit hour) marked')),
                ('load_exam_credit', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Load hours per exam credit hour')),
                ('load_exam_marked', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Load hours per exam marked')),
                ('load_fte_misc', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Staff misc. load per FTE fraction')),
                ('hours_fte', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name="Backstop 'hours per FTE' value")),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Standard Load',
                'verbose_name_plural': 'Standard Loads',
                'ordering': ['-year'],
                'get_latest_by': 'year',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bill_for', models.CharField(max_length=100)),
                ('issue_date', models.DateField()),
                ('due_date', models.DateField()),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(max_length=10)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'transaction',
                'verbose_name_plural': 'transactions',
            },
        ),
        migrations.CreateModel(
            name='HistoricalTaskSchool',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('number_needed', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('load_fixed', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Fixed load hours')),
                ('load_fixed_first', models.FloatField(blank=True, default=0.0, null=True, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Fixed load hours (first time)')),
                ('load', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('load_first', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('students', models.IntegerField(blank=True, help_text='Number of students for scaling load', null=True)),
                ('notes', models.TextField(blank=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('load_function', models.ForeignKey(blank=True, db_constraint=False, help_text='Function by which student load for this task scales', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='app.loadfunction')),
            ],
            options={
                'verbose_name': 'historical Departmental Task',
                'verbose_name_plural': 'historical Departmental Tasks',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=16, unique=True)),
                ('name', models.CharField(max_length=128, unique=True)),
                ('has_dissertation', models.BooleanField(default=False)),
                ('has_placement', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True)),
                ('students', models.IntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('credit_hours', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Credit Hours')),
                ('lectures', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Lectures')),
                ('problem_classes', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Problem Classes')),
                ('coursework', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Coursework Prepared')),
                ('synoptic_lectures', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Synoptic Lectures')),
                ('exams', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Exams')),
                ('exam_mark_fraction', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], verbose_name='Exam fraction of total mark')),
                ('coursework_mark_fraction', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], verbose_name='Coursework fraction of total mark')),
                ('notes', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('academic_group', models.ForeignKey(blank=True, help_text='The group, if any, responsible for this module', null=True, on_delete=django.db.models.deletion.PROTECT, to='app.academicgroup', verbose_name='Group')),
            ],
            options={
                'verbose_name': 'Module',
                'verbose_name_plural': 'Modules',
                'ordering': ['name'],
            },
            managers=[
                ('objects_active', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalTaskModule',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('number_needed', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('load_fixed', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Fixed load hours')),
                ('load_fixed_first', models.FloatField(blank=True, default=0.0, null=True, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Extra load hours for first-time')),
                ('students', models.IntegerField(blank=True, help_text='Number of students for scaling load, if not the whole module', null=True)),
                ('coursework_fraction', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)], verbose_name='Fraction of coursework marked')),
                ('exam_fraction', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)], verbose_name='Fraction of exams marked')),
                ('notes', models.TextField(blank=True)),
                ('load', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('load_first', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('load_function', models.ForeignKey(blank=True, db_constraint=False, help_text='Function by which student load for this task scales', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='app.loadfunction')),
                ('module', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='app.module')),
            ],
            options={
                'verbose_name': 'historical Module Task',
                'verbose_name_plural': 'historical Module Tasks',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=16, unique=True)),
                ('name', models.CharField(max_length=128)),
                ('gender', models.CharField(help_text='Single-letter code', max_length=1)),
                ('type', models.CharField(max_length=16)),
                ('notes', models.TextField(blank=True)),
                ('load_calculated_target', models.FloatField(blank=True, help_text='Target load hours', null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('load_calculated_worked', models.FloatField(blank=True, help_text='Worked load hours', null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('load_balance', models.FloatField(default=0, help_text='Ongoing load balance')),
                ('hours_fixed', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(2000)], verbose_name='Fixed hours (non-FTE)')),
                ('fte_fraction', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], verbose_name='FTE fraction')),
                ('is_active', models.BooleanField(default=True)),
                ('academic_group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.academicgroup', verbose_name='Group')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Staff Member',
                'verbose_name_plural': 'Staff Members',
                'ordering': ('is_active', 'name'),
            },
            managers=[
                ('objects_active', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='TaskModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('number_needed', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('load_fixed', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Fixed load hours')),
                ('load_fixed_first', models.FloatField(blank=True, default=0.0, null=True, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Extra load hours for first-time')),
                ('students', models.IntegerField(blank=True, help_text='Number of students for scaling load, if not the whole module', null=True)),
                ('coursework_fraction', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)], verbose_name='Fraction of coursework marked')),
                ('exam_fraction', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)], verbose_name='Fraction of exams marked')),
                ('notes', models.TextField(blank=True)),
                ('load', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('load_first', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('load_function', models.ForeignKey(blank=True, help_text='Function by which student load for this task scales', null=True, on_delete=django.db.models.deletion.PROTECT, to='app.loadfunction')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.module')),
            ],
            options={
                'verbose_name': 'Module Task',
                'verbose_name_plural': 'Module Tasks',
                'ordering': ('is_active', 'module', 'name'),
            },
            managers=[
                ('objects_active', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='AssignmentModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True)),
                ('is_first_time', models.BooleanField(default=False)),
                ('is_provisional', models.BooleanField(default=False)),
                ('staff', models.ForeignKey(limit_choices_to={'is_active': True}, on_delete=django.db.models.deletion.PROTECT, to='app.staff')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.taskmodule')),
            ],
            options={
                'verbose_name': 'Module Assignment',
                'verbose_name_plural': 'Module Assignments',
                'ordering': ('-staff', 'task'),
            },
        ),
        migrations.CreateModel(
            name='TaskSchool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('number_needed', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('load_fixed', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Fixed load hours')),
                ('load_fixed_first', models.FloatField(blank=True, default=0.0, null=True, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Fixed load hours (first time)')),
                ('load', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('load_first', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('students', models.IntegerField(blank=True, help_text='Number of students for scaling load', null=True)),
                ('notes', models.TextField(blank=True)),
                ('load_function', models.ForeignKey(blank=True, help_text='Function by which student load for this task scales', null=True, on_delete=django.db.models.deletion.PROTECT, to='app.loadfunction')),
            ],
            options={
                'verbose_name': 'Departmental Task',
                'verbose_name_plural': 'Departmental Tasks',
                'ordering': ('is_active', 'name'),
            },
            managers=[
                ('objects_active', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='AssignmentSchool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True)),
                ('is_first_time', models.BooleanField(default=False)),
                ('is_provisional', models.BooleanField(default=False)),
                ('staff', models.ForeignKey(limit_choices_to={'is_active': True}, on_delete=django.db.models.deletion.PROTECT, to='app.staff')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.taskschool')),
            ],
            options={
                'verbose_name': 'School Assignment',
                'verbose_name_plural': 'School Assignments',
                'ordering': ('-staff', 'task'),
            },
        ),
        migrations.AddIndex(
            model_name='module',
            index=models.Index(fields=['code'], name='app_module_code_b3bfa8_idx'),
        ),
        migrations.AddIndex(
            model_name='staff',
            index=models.Index(fields=['name'], name='app_staff_name_1f0f0e_idx'),
        ),
        migrations.AddIndex(
            model_name='staff',
            index=models.Index(fields=['gender'], name='app_staff_gender_934f77_idx'),
        ),
        migrations.AddIndex(
            model_name='staff',
            index=models.Index(fields=['academic_group'], name='app_staff_academi_c31d47_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='assignmentmodule',
            unique_together={('task', 'staff')},
        ),
        migrations.AlterUniqueTogether(
            name='assignmentschool',
            unique_together={('task', 'staff')},
        ),
    ]
