# Generated by Django 3.2 on 2021-05-20 15:10

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Mark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Research',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=20, null=True)),
                ('create_date', models.DateTimeField(default=datetime.datetime(2021, 5, 20, 15, 10, 52, 591639, tzinfo=utc))),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('recruit_start', models.DateTimeField()),
                ('recruit_end', models.DateTimeField()),
                ('capacity', models.IntegerField()),
                ('current_number', models.IntegerField(default=0)),
                ('mark_users', models.ManyToManyField(blank=True, related_name='marked_research', through='research.Mark', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TagResearch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('researches', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='research.research')),
                ('tags', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='research.tag')),
            ],
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reward_type', models.CharField(max_length=50)),
                ('amount', models.IntegerField()),
                ('research', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='research.research')),
            ],
        ),
        migrations.CreateModel(
            name='ResearcheeResearch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('researchees', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.researchee')),
                ('researches', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='research.research')),
            ],
        ),
        migrations.AddField(
            model_name='research',
            name='researchees',
            field=models.ManyToManyField(through='research.ResearcheeResearch', to='accounts.Researchee'),
        ),
        migrations.AddField(
            model_name='research',
            name='researcher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='researches', to='accounts.researcher'),
        ),
        migrations.AddField(
            model_name='research',
            name='tag',
            field=models.ManyToManyField(blank=True, related_name='researches', through='research.TagResearch', to='research.Tag'),
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('body', models.TextField()),
                ('image', models.ImageField(blank=True, upload_to='')),
                ('research', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='research.research')),
            ],
        ),
        migrations.AddField(
            model_name='mark',
            name='research',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='research.research'),
        ),
        migrations.AddField(
            model_name='mark',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]