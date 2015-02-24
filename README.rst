=======
FUN-CMD
=======

A command-line tool for OpenFUN.

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
