# Generated by Django 4.0.1 on 2022-01-05 11:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('audio_recorder', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='utterances',
            old_name='utterances',
            new_name='utterance',
        ),
    ]
