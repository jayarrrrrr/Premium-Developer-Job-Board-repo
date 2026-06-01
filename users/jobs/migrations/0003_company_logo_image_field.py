# Generated migration for changing Company.logo from URLField to ImageField

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_company_job_application_savedjob'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='logo',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='company_logos/'
            ),
        ),
    ]
