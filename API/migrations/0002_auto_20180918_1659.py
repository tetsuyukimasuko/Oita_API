# Generated by Django 2.0.2 on 2018-09-18 07:59

import API.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', API.models.MyUserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='billing_target',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='API.Tenant', verbose_name='請求先テナント'),
        ),
    ]
