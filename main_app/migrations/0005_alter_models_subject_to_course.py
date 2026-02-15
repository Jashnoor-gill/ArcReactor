# Generated migration - Subject to Course conversion
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_course_course_code'),
    ]

    operations = [
        # Attendance model changes
        migrations.AlterField(
            model_name='attendance',
            name='subject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='main_app.course'),
        ),
        migrations.RenameField(
            model_name='attendance',
            old_name='subject',
            new_name='course',
        ),
        # StudentResult model changes
        migrations.AddField(
            model_name='studentresult',
            name='test_1',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='studentresult',
            name='test_2',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='studentresult',
            name='test_3',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='studentresult',
            name='mid_sem',
            field=models.FloatField(default=0),
        ),
        # Rename test to test_1 (this will be handled by data migration if needed)
        migrations.RenameField(
            model_name='studentresult',
            old_name='test',
            new_name='test_1_temp',
        ),
        # Change subject to course in StudentResult
        migrations.AlterField(
            model_name='studentresult',
            name='subject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.course'),
        ),
        migrations.RenameField(
            model_name='studentresult',
            old_name='subject',
            new_name='course',
        ),
    ]
