from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from core.models import Training


class Command(BaseCommand):
    help = 'Блокировка тренировок старше LOCK_DAYS дней (по умолчанию 30)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=getattr(settings, 'LOCK_DAYS', 30),
            help='Количество дней до блокировки',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Только показать, сколько записей будет заблокировано',
        )

    def handle(self, *args, **options):
        days = options['days']
        cutoff = date.today() - timedelta(days=days)

        qs = Training.objects.filter(date__lt=cutoff, is_locked=False)
        count = qs.count()

        if options['dry_run']:
            self.stdout.write(f'Будет заблокировано записей: {count} (дата < {cutoff})')
            return

        with transaction.atomic():
            updated = qs.update(is_locked=True)

        self.stdout.write(
            self.style.SUCCESS(f'✓ Заблокировано записей: {updated} (дата < {cutoff})')
        )
