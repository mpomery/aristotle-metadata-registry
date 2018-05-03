"""
Aristotle Easy Installer

This script guides you through the setup of the Aristotle Metadata Registry.

Run install --help for help text
"""
from __future__ import unicode_literals, print_function


import os
import re
import sys
from subprocess import call
from random import getrandbits
import hashlib
import shutil
import argparse
import zipfile


BASE_DIR = os.path.dirname(__file__)
name = "newly created"  # Forward-declaration placeholder
PIP_MSG = "You can finish installing by running - pip install -r requirements.txt - from the %s directory" % name


optional_modules = [
    ("Aristotle Glossary Extension", "#!aristotle_glossary!"),
    ("Aristotle Dataset Extensions", "#!aristotle_dse!"),
    ("Aristotle DDI Downloaders", "#!aristotle_ddi_utils!"),
    ("Aristotle MDR API", "#!aristotle_mdr_api!")
]


def valid_input(prompt, match):

    try:
        # Ensure input compatability across Python 2/3
        input_func = vars(__builtins__).get('raw_input', input)
    except:
        pass
    for i in range(5):
        check = input_func(prompt)
        if re.match(match, check):
            return check
    raise Exception


def setup_mdr(args):
    name_regex = '^[a-z][a-z_]*$'
    yn = '^[YyNn]?$'  # yes/no regex

    if not args.name or not re.match(name_regex, args.name[0]):
        name = valid_input("Enter the system name for your registry (lowercase letters and underscores ONLY): ", name_regex)
    else:
        name = args.name

    if not args.directory or args.directory[0] == '.':
        directory = os.getcwd()
    else:
        directory = args.directory[0]


    use_existing_files = check_example_exists(directory, name, yn)

    if not use_existing_files:

        if args.force_dl:
            copied = False
        else:
            try:
                copied = copy_example_mdr(directory)
            except:
                print("Copying Example registy failed")
                raise

        if not copied:
            # if not args.force_dl:
            #     print('Copying Registry Failed, Downloading registry')
            download_example_mdr(directory)

        rename_example_mdr(name, directory)

    extensions = []

    do_install = valid_input("Do you wish to install any additional Aristotle modules? (y/n): ", yn).lower()
    if do_install == 'y':
        print("Select extensions to install (y/n)")
        for display, ext_token in optional_modules:
            do_ext = valid_input("  %s: " % display, yn).lower()
            if do_ext == 'y':
                extensions.append(ext_token)

    if extensions:
        find_and_remove(directory, extensions)

    # Update the settings key
    generate_secret_key(name, directory)

    if args.dry_install:
        print("Performing dry run, no requirements installed.")
        print(PIP_MSG)
        return 0
    elif args.force_install:
        print("Installing from requirements.txt")
        do_install = True
    else:
        do_install = 'y' == valid_input("Ready to install requirements? (y/n): ", yn).lower()
        if not do_install:
            print("Performing dry run, no requirements installed.")
            print(PIP_MSG)

    if do_install:
        try:
            install_reqs(name, directory)
        except:
            print("Installing requirements failed.")
            print(PIP_MSG)
            raise

    if not args.dry_install:
        print("Running django management commands")
        result = manage_commands(name, directory)
        print("You can now locally test your installed registry by running the command './manage.py runserver'")

    print('Done! Your registry was installed in %s' % directory)

def generate_secret_key(name, directory):
    key = "Change-this-key-as-soon-as-you-can"
    # This is probably not cryptographically secure, not for production.
    gen_key = hashlib.sha224(str(getrandbits(128)).encode('utf-8')).hexdigest()
    fname = '%s/%s/settings.py' % (name, name)
    fpath = os.path.join(directory, fname)
    with open(fpath) as f:
        s = f.read()
    s = s.replace(key, gen_key)
    with open(fpath, "w") as f:
        f.write(s)


def rename_example_mdr(name, directory):
    startpath = os.path.join(directory, 'example_mdr')

    os.rename(os.path.join(startpath, 'example_mdr'), os.path.join(startpath, name))
    os.rename(startpath, os.path.join(directory, name))
    find_and_replace(directory, 'example_mdr', name)


def install_reqs(name, dir):
    # pip.main(['install', package])
    reqfile = os.path.join(dir, '%s/requirements.txt' % name)
    result = call(["pip", 'install', '-r%s' % reqfile])
    return result


def manage_commands(name, dir):
    manage_path = os.path.join(dir, '%s/manage.py' % name)
    migrate = call(["python3", manage_path, 'migrate'])
    cstatic = call(["python3", manage_path, 'collectstatic'])
    cctable = call(["python3", manage_path, 'createcachetable'])
    return (migrate, cstatic, cctable)

def check_example_exists(dir, name, yn):

    dest = os.path.join(dir, name)
    if os.path.isdir(dest):
        print('The example_mdr folder is already at %s' % dest)
        use_existing = 'y' == valid_input("Would you like to use the existing files? They will be deleted otherwise (y/n): ", yn).lower()
        if use_existing:
            return True
        else:
            you_sure = 'y' == valid_input("Are you sure you want to delete the directory at %s (y/n):" % dest, yn).lower()
            if you_sure:
                print('Deleting existing example_mdr')
                shutil.rmtree(dest)
                return False
            else:
                print('Using existing files')
                return True

    return False

def download_example_mdr(directory):

    try:
        import requests
    except ImportError:
        print('requests must be installed to download the example registry')
        print('run \"pip install requests\" to install')
        raise

    print("Attempting to retrieve example registry")
    url = "https://s3-ap-southeast-2.amazonaws.com/aristotle-mdr/example_mdr.zip"
    response = requests.get(url)
    dest = os.path.join(directory, 'example_mdr.zip')
    with open(dest, 'wb') as f:
        f.write(response.content)

    zip = zipfile.ZipFile(dest)
    zip.extractall(directory)
    os.remove(dest)

    return True


def copy_example_mdr(dir):
    print("Copying in example metadata registry")
    source = os.path.join(BASE_DIR, 'example_mdr')
    dest = os.path.join(dir, 'example_mdr')

    if os.path.isdir(source):
        shutil.copytree(source, dest)
        return True

    return False


def find_and_replace(mydir, old, new):
    """Really naive find and replace lovingly borrowed from stack overflow - http://stackoverflow.com/a/4205918/764357"""
    for dname, dirs, files in os.walk(mydir):
        for fname in files:
            if fname.endswith(('py', 'txt', 'rst')):
                fpath = os.path.join(dname, fname)
                with open(fpath) as f:
                    s = f.read()
                s = s.replace(old, new)
                with open(fpath, "w") as f:
                    f.write(s)


def find_and_remove(mydir, extensions):
    for dname, dirs, files in os.walk(mydir):
        for fname in files:
            if fname.endswith(('py', 'txt', 'rst')):
                fpath = os.path.join(dname, fname)
                with open(fpath) as f:
                    s = f.read()
                for ext in extensions:
                    s = s.replace(ext, '')
                with open(fpath, "w") as f:
                    f.write(s)

def main(argv=None):

    parser = argparse.ArgumentParser(description='Install Aristotle Example Registry')
    parser.add_argument('-n', '--name', nargs=1, default='', type=str, dest='name', help='Registry Name')
    parser.add_argument('-f', '--force', action='store_true', default=False, dest='force_install', help='Force Requirements Install (instead of asking)')
    parser.add_argument('-d', '--dry', action='store_true', default=False, dest='dry_install', help='Dry Install (do dependancies installed or management commands run)')
    parser.add_argument('--dl', '--download', action='store_true', default=False, dest='force_dl', help='Force the registry to be downloaded instead of copied from package')
    parser.add_argument('--dir', nargs=1, default='.', dest='directory', help='Directory to install the registry (default: current directory)')

    args = parser.parse_args()

    return setup_mdr(args)

if __name__ == "__main__":
    sys.exit(main())
