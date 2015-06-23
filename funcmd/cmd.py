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
        return ['runserver', '--traceback', '0.0.0.0:{}'.format(port)] + args[1:]
    elif args[0] == "assets":
        update_assets()
        return None
    elif args[0] == "requirements":
        install_prerequirements()
        return None
    elif args[0] == "test":
        check_test_settings(settings)
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
    PYTHON_REQ_FILES = pavelib.prereqs.PYTHON_REQ_FILES + [
        "../fun-apps/requirements/base.txt",
        "../fun-apps/requirements/dev.txt",
    ]
    def install_edx_and_fun_requirements():
        from paver.easy import sh
        for req_file in PYTHON_REQ_FILES:
            sh("pip install -q --exists-action w -r {req_file}".format(req_file=req_file))
    pavelib.prereqs.prereq_cache("Python prereqs", PYTHON_REQ_FILES, install_edx_and_fun_requirements)

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

def check_test_settings(settings):
    if "test" not in settings:
        print ("""Trying to run tests with non-test settings."""
               """ It's dangerous and you probably don't want to do that.""")
        sys.exit(1)

def execute_manage_command(*arguments):
    """Run manage.py command"""
    import django.core.management
    django.core.management.execute_from_command_line(["manage.py"] + list(arguments))

