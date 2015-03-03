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

Start an lms instance::

    fun lms.dev run

If you don't wish to update all assets::

    fun lms.dev run --fast

Contribute
==========

Don't forget to run (and write) tests::

    nosetests
