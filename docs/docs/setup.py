from setuptools import setup

setup(name='dpy_toolbox',
      version='0.0.9',
      description="Discord.py simplifier",
      long_description="",
      author='TheWever',
      author_email='nonarrator@gmail.com',
      license='MIT',
      packages=['dpy_toolbox'],
      zip_safe=False,
      install_requires=[
            'git+https://github.com/Rapptz/discord.py#egg=discord-py',
            'sphinxcontrib_trio'
          ]
      )