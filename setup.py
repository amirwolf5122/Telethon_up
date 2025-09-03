from setuptools import setup, find_packages
with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name="telethon_up",
    version="1.0.1",
    description="Full-featured Telegram client library for Python 3",
    packages=find_packages(),
    install_requires=[],
    author="Amir:3",
    author_email="amirwolf512@gmail.com",
    license='MIT',
    python_requires='>=3.5',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Communications :: Chat',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='telegram api chat client library messaging mtproto',
)
