from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='reminder_sent',
            field=models.BooleanField(default=False, verbose_name='Lembrete enviado'),
        ),
    ]