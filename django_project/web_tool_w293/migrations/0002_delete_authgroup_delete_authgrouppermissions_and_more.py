# Generated by Django 4.1 on 2024-10-01 09:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("web_tool_w293", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="AuthGroup",
        ),
        migrations.DeleteModel(
            name="AuthGroupPermissions",
        ),
        migrations.DeleteModel(
            name="AuthPermission",
        ),
        migrations.DeleteModel(
            name="AuthUser",
        ),
        migrations.DeleteModel(
            name="AuthUserGroups",
        ),
        migrations.DeleteModel(
            name="AuthUserUserPermissions",
        ),
        migrations.DeleteModel(
            name="DjangoAdminLog",
        ),
        migrations.DeleteModel(
            name="DjangoContentType",
        ),
        migrations.DeleteModel(
            name="DjangoMigrations",
        ),
        migrations.DeleteModel(
            name="DjangoSession",
        ),
        migrations.DeleteModel(
            name="Gene",
        ),
        migrations.DeleteModel(
            name="W293",
        ),
        migrations.DeleteModel(
            name="WebToolUser",
        ),
    ]
