# Generated by Django 5.0.3 on 2025-03-20 14:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_staller_payr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitems',
            name='foo_cat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.foo_category'),
        ),
    ]
