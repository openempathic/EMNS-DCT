# Generated by Django 4.2.2 on 2023-06-28 11:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(default='media/default.jpg', upload_to='media/profile_picks')),
                ('status', models.CharField(choices=[('Admin', 'Admin'), ('Actor', 'Actor'), ('Viewer', 'Viewer'), ('NLD', 'NLD')], default='Viewer', max_length=70, null=True)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Other', max_length=70, null=True)),
                ('age', models.IntegerField(default=0)),
                ('healthcare', models.CharField(choices=[('Psychologist', 'Psychologist'), ('Psychatrist', 'Psychatrist'), ('Other physician', 'Other physician')], max_length=70, null=True)),
                ('institute', models.CharField(default='Not Specified', max_length=70, null=True)),
                ('experience', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
