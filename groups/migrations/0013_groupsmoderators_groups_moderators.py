# Generated by Django 4.1.7 on 2023-03-31 13:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0012_remove_groups_moderators'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupsModerators',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('privilege', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.groups')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='groups',
            name='moderators',
            field=models.ManyToManyField(related_name='group_moderator', through='groups.GroupsModerators', to=settings.AUTH_USER_MODEL),
        ),
    ]
