import os
import subprocess
from datetime import date
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Создание SQL-дампа базы данных PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            default=str(settings.BASE_DIR / 'backups'),
            help='Директория для сохранения дампа',
        )

    def handle(self, *args, **options):
        db = settings.DATABASES['default']
        output_dir = options['output_dir']
        os.makedirs(output_dir, exist_ok=True)

        filename = f'sultan_{date.today().isoformat()}.sql'
        filepath = os.path.join(output_dir, filename)

        env = os.environ.copy()
        env['PGPASSWORD'] = db.get('PASSWORD', '')

        cmd = [
            'pg_dump',
            '-h', db.get('HOST', 'localhost'),
            '-p', str(db.get('PORT', 5432)),
            '-U', db.get('USER', 'postgres'),
            '-d', db.get('NAME', ''),
            '-f', filepath,
            '--no-password',
        ]

        try:
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                size = os.path.getsize(filepath)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Резервная копия создана: {filepath} ({size // 1024} KB)')
                )
            else:
                self.stderr.write(f'Ошибка pg_dump: {result.stderr}')
        except FileNotFoundError:
            self.stderr.write('pg_dump не найден. Убедитесь, что PostgreSQL установлен и pg_dump доступен в PATH.')
        except subprocess.TimeoutExpired:
            self.stderr.write('Время ожидания pg_dump истекло.')
