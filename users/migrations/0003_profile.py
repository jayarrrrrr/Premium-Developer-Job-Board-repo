from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_add_premium_dates'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('ADMIN', 'Admin'), ('EMPLOYER', 'Employer'), ('JOB_SEEKER', 'Job Seeker')], default='JOB_SEEKER', max_length=20)),
                ('is_premium', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='profile', to='users.user')),
            ],
        ),
    ]
