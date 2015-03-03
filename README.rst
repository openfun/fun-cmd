=======
FUN-CMD
=======

A command-line tool for OpenFUN. fun-cmd was designed as a helpful tool to run
frequently-used OpendEdx commands in development and test modes.

Install
=======

You should install fun-cmd in your OpenEdx virtual box::

    pip install git+https://github.com/openfun/fun-cmd.git@master#egg=fun-cmd


Available commands
==================

Run all fun-apps tests::

    fun lms.test test ../fun-apps

Run tests from a FUN application::

    fun lms.test test ../fun-apps/backoffice

Start a shell::

    fun lms.dev shell

Install requirements (including FUN requirements)::

    fun lms.dev requirements

Process assets, static collection::

    fun lms.dev assets

Install requirements, process assets and start an lms instance::

    fun lms.dev run

If you just want to run the lms instance::

    fun lms.dev run --fast

Contribute
==========

Don't forget to run (and write) tests::

    nosetests
