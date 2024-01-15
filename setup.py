from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in liqpay_app/__init__.py
from liqpay_app import __version__ as version

setup(
	name="liqpay_app",
	version=version,
	description="This app must simplify a frappe-liqpay integration",
	author="ikrok",
	author_email="kubliy.n@ikrok.net",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
