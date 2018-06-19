#!/usr/bin/python3

import os
import sys

if __name__ == "__main__":
    if 'test' in sys.argv:
        testindex = sys.argv.index('test')
        after = sys.argv[testindex+1]

        module = after.split('.')[0]

        print(module)

        if module == 'aristotle_mdr':
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aristotle_mdr.tests.settings.settings")
        else:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", module + ".tests.settings")

    elif 'schemamigration' in sys.argv:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aristotle_mdr.tests.settings.settings")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aristotle_mdr.required_settings")

    from django.core.management import execute_from_command_line

execute_from_command_line(sys.argv)
