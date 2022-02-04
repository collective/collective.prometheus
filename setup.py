from setuptools import setup, find_packages
from os.path import join
import sys

version = '1.6.1'
readme = open("README.rst").read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = ['setuptools']
if sys.version_info < (2, 5):
    install_requires.append('threadframe')

setup(
    name='collective.prometheus',
    version=version,
    description='Prometheus integration for Zope/Plone.',
    long_description=readme[readme.find('\n\n'):] + '\n' + history,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Plone',
        'Framework :: ZODB',
        'Framework :: Zope2',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='plone zope prometheus monitoring',
    author='Rob McBroom',
    author_email='rob@sixfeetup.com',
    url='https://github.com/collective/collective.prometheus',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['collective'],
    include_package_data=True,
    platforms='Any',
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'zserver': ['Products.ZServerViews>=0.2'],
        'test': ['plone.app.testing'],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
