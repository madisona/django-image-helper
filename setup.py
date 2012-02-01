
from setuptools import setup, find_packages

REQUIREMENTS = (
    'django>=1.3',
    'PIL',
)

from image_helper import VERSION

setup(
    name="django-image-helper",
    version=VERSION,
    author="Aaron Madison",
    description="Django helpers for working with images.",
    long_description=open('README', 'r').read(),
    url="https://github.com/madisona/django-image-helper",
    packages=find_packages(exclude=["example"]),
    install_requires=REQUIREMENTS,
    zip_safe=False,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)
