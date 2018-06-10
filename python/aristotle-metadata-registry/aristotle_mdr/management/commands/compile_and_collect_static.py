import os
from tempfile import mkdtemp

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from django.test import override_settings
import static_precompiler


class Command(BaseCommand):
    args = ''
    help = 'Compiles and Collects all staticfiles into the static path'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--noinput",
            default=False,
            action='store_true',
        )

    def handle(self, *args, **options):
        compile_dir = options.get('output_path', mkdtemp())
        print(compile_dir)

        with override_settings(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            }
        ):
            call_command('migrate', 'static_precompiler')

            with override_settings(
                STATICFILES_FINDERS=(
                    'django.contrib.staticfiles.finders.FileSystemFinder',
                    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
                    'static_precompiler.finders.StaticPrecompilerFinder',
                ),
            ):
                static_precompiler.settings.OUTPUT_DIR = os.path.join(
                    compile_dir,
                    getattr(settings, 'STATIC_PRECOMPILER_OUTPUT_DIR', 'COMPILED')
                )
                call_command('compilestatic')

            with override_settings(
                STATICFILES_DIRS=[compile_dir],
                DEBUG=False,  # We need this off for manifest to work
                STATICFILES_FINDERS=(
                    'django.contrib.staticfiles.finders.FileSystemFinder',
                    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
                ),
            ):
                call_command('collectstatic', '--noinput', verbosity=3)

        print('All done!')
