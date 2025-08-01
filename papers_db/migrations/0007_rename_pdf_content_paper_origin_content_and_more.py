# Generated by Django 5.2.2 on 2025-07-14 11:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('papers_db', '0006_alter_paper_markdown_content'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paper',
            old_name='pdf_content',
            new_name='origin_content',
        ),
        migrations.RenameField(
            model_name='paper',
            old_name='pdf_filemd5',
            new_name='origin_filemd5',
        ),
        migrations.RenameField(
            model_name='paper',
            old_name='pdf_filename',
            new_name='origin_filename',
        ),
        migrations.AddField(
            model_name='paper',
            name='origin_filelink',
            field=models.URLField(blank=True, help_text='Original URL of the file (optional)', null=True, validators=[django.core.validators.URLValidator()]),
        ),
        migrations.AddIndex(
            model_name='paper',
            index=models.Index(fields=['origin_filemd5'], name='papers_origin__b7430f_idx'),
        ),
        migrations.AddIndex(
            model_name='paper',
            index=models.Index(fields=['is_active'], name='papers_is_acti_61c2c5_idx'),
        ),
        migrations.AddIndex(
            model_name='paper',
            index=models.Index(fields=['origin_filemd5', 'is_active'], name='papers_origin__be9870_idx'),
        ),
    ]
