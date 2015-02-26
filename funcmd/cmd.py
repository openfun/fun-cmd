from .tools import defuse_xml, disable_contracts
defuse_xml()# This must be done early
disable_contracts()

import argparse
import importlib
import os
import sys

def fun():
    fun_args, django_args = parse_args()
    settings, service = get_environment(fun_args.settings)
    setup_environment(settings, service)

    if django_args[0] == "run":
        if "--fast" in django_args:
            django_args.remove('--fast')
        else:
            update_assets()
        port = 8000 if service == "lms" else 8001
        command = ['manage.py', 'runserver', '--traceback', '0.0.0.0:{}'.format(port)] + django_args[1:]
    else:
        command = ['manage.py'] + django_args
    execute_from_command_line(command)

def execute_from_command_line(command):
    import django.core.management
    django.core.management.execute_from_command_line(command)

def update_assets():
    import pavelib.assets

    # Compile templated SASS (compile_templated_sass)
    print "---> preprocess_assets"
    execute_from_command_line(["manage.py", "preprocess_assets"])

    pavelib.assets.process_xmodule_assets()
    pavelib.assets.compile_coffeescript()
    pavelib.assets.compile_sass(False)

def parse_args():
    parser = argparse.ArgumentParser(description="Run FUN services")
    parser.add_argument(
        "settings",
        help=("Settings module to use. If it starts with 'edx', it will be"
              " relative to edx-platform. If it starts with 'prod', it will be"
              " relative to fun-config. Otherwise it will be relative to"
              " fun-apps/envs. E.g: lms.dev, prod.lms_platform,"
              " edx.cms.envs.dev."
              " The service to use (lms or cms) will be inferred from the"
              "settings module.")
    )

    fun_args, django_args = parser.parse_known_args()
    return fun_args, django_args

def get_environment(partial_settings):
    service = get_service(partial_settings)

    if partial_settings.startswith('edx.'):
        settings = "{service}.envs.{env}"
        env = partial_settings[4:]
    elif partial_settings.startswith('prod.'):
        settings = "funconfig.{env}"
        env = partial_settings[5:]
    else:
        settings = "fun.envs.{service}.{env}"
        env = partial_settings[4:]
    settings = settings.format(service=service, env=env)
    return settings, service

def get_service(settings):
    if 'lms' in settings:
        return 'lms'
    elif 'cms' in settings:
        return 'cms'
    else:
        raise ValueError("Could not determine the service variant to use")

def setup_environment(settings, service):
    sys.path.insert(0, '/edx/app/edxapp/edx-platform')
    sys.path.append('/edx/app/edxapp/fun-apps')

    os.environ["DJANGO_SETTINGS_MODULE"] = settings
    os.environ.setdefault("SERVICE_VARIANT", service)

    startup_module = "{service}.startup".format(service=service)
    startup = importlib.import_module(startup_module)
    startup.run()
