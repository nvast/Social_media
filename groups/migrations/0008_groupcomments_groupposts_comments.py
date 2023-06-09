# Generated by Django 4.1.7 on 2023-03-29 11:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0007_alter_groups_posts'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupComments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=1000)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_post_comments', to='groups.groupposts')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_user_comments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='groupposts',
            name='comments',
            field=models.ManyToManyField(related_name='group_posts_comments', through='groups.GroupComments', to=settings.AUTH_USER_MODEL),
        ),
    ]
