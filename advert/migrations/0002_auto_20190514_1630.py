# Generated by Django 2.1.8 on 2019-05-14 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advert', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advert',
            name='book_title',
            field=models.CharField(db_index=True, max_length=250),
        ),
    ]