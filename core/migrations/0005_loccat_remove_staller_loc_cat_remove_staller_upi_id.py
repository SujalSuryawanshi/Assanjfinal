# Generated by Django 5.0.3 on 2025-03-29 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_menuitems_foo_cat'),
    ]

    operations = [
        migrations.CreateModel(
            name='Loccat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=1000, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='staller',
            name='loc_cat',
        ),
        migrations.RemoveField(
            model_name='staller',
            name='upi_id',
        ),
    ]
