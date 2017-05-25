"ECS Deploy"
from setuptools import find_packages, setup
from ecsdeploy import __version__

def read_file(path):
    result = []
    try:
        with open(path) as f:
            result = f.readlines()
    except Exception as err:
        pass
    return result

install_requires = read_file('requirements.txt')
tests_require = read_file('test-requirements.txt')

name = 'ecsdeploy'

setup(
    name=name,
    py_modules=[name],
    version=__version__,
    description='ECS Deploy',
    company='Symantec',
    author='Alexey Dubkov',
    author_email='alexey_dubkov@symantec.com',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    # for debug:
    #test_suite="amibuilder.tests",
    test_suite="nose.collector",
    entry_points={
        "console_scripts":[
            'ecsdeploy = ecsdeploy.ecsdeploy:main',
        ]
    },
)
