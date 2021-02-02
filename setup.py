from setuptools import find_packages
from setuptools import setup


setup(
    name="django-utils",
    version="0.1",
    license="",
    url="https://github.com/4teamwork/django-utils",
    author="4teamwork AG",
    author_email="mailto:info@4teamwork.ch",
    maintainer="4teamwork AG",
    maintainer_email="mailto:info@4teamwork.ch",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.6.*, <4",
    install_requires=[
        "django-configurations",
        "sentry-sdk",
    ],
    setup_requires=[
        "black>=20.8b1",
    ],
)
