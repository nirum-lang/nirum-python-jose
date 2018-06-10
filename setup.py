from setuptools import setup


def readme():
    try:
        with open('README.rst') as r, open('CHANGES.rst') as c:
            return r.read() + '\n\n' + c.read()
    except IOError:
        pass


setup(
    # The most metadata go to setup.cfg file as possible.
    long_description=readme(),
)
