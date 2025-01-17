# Generated by Django 3.2.14 on 2022-12-08 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_auto_20190116_0323'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrgSAMLConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('org_id', models.IntegerField(unique=True)),
                ('metadata_url', models.TextField()),
                ('single_sign_on_service', models.TextField()),
                ('single_logout_service', models.TextField()),
                ('valid_days', models.IntegerField()),
            ],
            options={
                'db_table': 'org_saml_config',
            },
        ),
    ]
