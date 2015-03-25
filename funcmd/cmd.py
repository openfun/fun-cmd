from .tools import defuse_xml, disable_contracts
defuse_xml()# This must be done early
disable_contracts()

import argparse
import importlib
import os
import sys

def fun():
    fun_args, other_args = parse_args()
    settings, service = get_environment(fun_args.settings)
    setup_environment(settings, service)
    run_command(settings, service, fun_args, other_args)

def parse_args():
    parser = argparse.ArgumentParser(description="Run FUN services", add_help=False)
    parser.add_argument("-h", "--help", action="store_true", help='show this help message and exit')
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

    fun_args, other_args = parser.parse_known_args()
    if fun_args.help:
        parser.print_help()
        print "========================"
        other_args.append("--help")
    return fun_args, other_args

def get_environment(partial_settings):
    """Get the full settings python path and the service to run.

    Returns:
        settings (str): python path pointing to the correct settings module.
        service (str): "lms" or "cms"
    """
    service = get_service(partial_settings)

    if partial_settings.startswith('edx.'):
        settings = "{service}.envs.{env}"
        env = partial_settings.split('.')[-1]
    elif partial_settings.startswith('prod.'):
        settings = "funconfig.{env}"
        env = partial_settings[5:]
    else:
        settings = "fun.envs.{service}.{env}"
        env = partial_settings[4:]
    settings = settings.format(service=service, env=env)
    return settings, service

def get_service(settings):
    """Get the service to run based on incomplete settings.

    Returns:
        service (str): "lms" or "cms"
    """
    if 'lms' in settings:
        return 'lms'
    elif 'cms' in settings:
        return 'cms'
    else:
        raise ValueError("Could not determine the service variant to use")

def setup_environment(settings, service):
    """Setup the sys.path and the environment variables required for the given service."""
    sys.path.insert(0, '/edx/app/edxapp/edx-platform')
    sys.path.append('/edx/app/edxapp/fun-apps')

    os.environ["DJANGO_SETTINGS_MODULE"] = settings
    os.environ.setdefault("SERVICE_VARIANT", service)

    startup_module = "{service}.startup".format(service=service)
    startup = importlib.import_module(startup_module)
    startup.run()

def run_command(settings, service, fun_args, other_args):
    """Run appropriate command for the given settings and service."""
    arguments = get_manage_command_arguments(settings, service, *other_args)
    if arguments:
        execute_manage_command(*arguments)

def get_manage_command_arguments(settings, service, *args):
    """Get arguments to pass to manage.py. Update assets if necessary."""
    if not args:
        return None
    args = list(args)
    if args[0] == "run":
        preprocess_runserver_arguments(args)
        port = 8000 if service == "lms" else 8001
        return ['runserver', '--traceback', '--skip-collect', '0.0.0.0:{}'.format(port)] + args[1:]
    elif args[0] == "assets":
        update_assets()
        return None
    elif args[0] == "requirements":
        install_prerequirements()
        return None
    else:
        return args

def preprocess_runserver_arguments(args):
    """
    Install prerequirements and update assets only if the server is not reloading.
    """
    if "--fast" in args:
        args.remove('--fast')
    else:
        if os.environ.get("RUN_MAIN") is None:
            install_prerequirements()
            update_assets()

def install_prerequirements():
    import pavelib.prereqs
    pavelib.prereqs.install_prereqs()
    fun_requirements = [
        "../fun-apps/requirements/base.txt",
        "../fun-apps/requirements/dm-xblock.txt",
        "../fun-apps/requirements/dev.txt",
    ]
    pavelib.prereqs.prereq_cache("FUN prereqs",
                                 fun_requirements,
                                 pavelib.prereqs.python_prereqs_installation)

def update_assets():
    """Run asset preprocessing, compilation, collection."""

    # Compile templated SASS (compile_templated_sass)
    print "---> preprocess_assets"
    execute_manage_command("preprocess_assets")

    import pavelib.assets
    pavelib.assets.process_xmodule_assets()
    pavelib.assets.compile_coffeescript()
    pavelib.assets.compile_sass(False)

    # Asset collection
    execute_manage_command("collectstatic", "--noinput")

def execute_manage_command(*arguments):
    """Run manage.py command"""
    import django.core.management
    django.core.management.execute_from_command_line(["manage.py"] + list(arguments))

