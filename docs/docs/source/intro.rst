:orphan:

.. currentmodule:: dpy-toolbox

.. _intro:

Introduction
==============

This is the documentation for dpy-toolbox, a library that extends the discord.py lib.

Prerequisites
---------------

dpy-toolbox only requires discord.py


.. _installing:

Installing
-----------
You can get the library directly from PyPI: ::

    python3 -m pip install -U dpy-toolbox


You can get discord.py also directly from PyPI: ::

    python3 -m pip install -U discord.py


A quick example:

.. code-block:: python3

    from dpy_toolbox import Bot

    class MyBot(Bot):
        async def on_ready(self):
            print(f'Logged on as {self.user}!')

        async def on_message(self, message):
            print(f'Message from {messsage.author}: {message.content}')

    bot = MyBot()
    bot.run('your token goes here')

