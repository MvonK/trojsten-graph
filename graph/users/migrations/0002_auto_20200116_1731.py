# Generated by Django 3.0.2 on 2020-01-16 17:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def migrate_suggestions(apps, schema_editor):
    Suggestion = apps.get_model('users', 'ContentSuggestion')
    Request = apps.get_model('users', 'ContentUpdateRequest')
    requests = [
        Request(
            status=s.status,
            content=s.suggestion,
            date_created=s.date_created,
            date_resolved=s.date_resolved,
            submitted_by=s.submitted_by
        )
        for s in Suggestion.objects.all()
    ]
    Request.objects.bulk_create(requests)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentUpdateRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Request'), (2, 'Accepted'), (3, 'Rejected')], default=1)),
                ('content', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_resolved', models.DateTimeField(blank=True, null=True)),
                ('submitted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='content_update_requests', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RunPython(migrate_suggestions, migrations.RunPython.noop),
        migrations.DeleteModel(
            name='ContentSuggestion',
        ),
    ]
