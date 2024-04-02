from setuptools import setup, find_packages

setup(
    name='src_file_translator',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        # Add dependencies here
        'googletrans>=3.1.0a0',
        'pysrt>=1.1.2'
    ],
    # Add other metadata (author, description, license, etc.)
)
