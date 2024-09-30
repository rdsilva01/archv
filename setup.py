from setuptools import setup, find_packages

setup(
    name='recomm',            
    version='0.1.0',                       # Version
    packages=find_packages(),              # Automatically find packages
    install_requires=[
        'requests',
        'beautifulsoup4',
        'publicnewsarchive',
        'clean-text',
        'yake',
        'spacy',
        'torch',
        'numpy',
        'transformers',
        'redis',
        'chunkipy',
    ],
    author='rdsilva01',                    # Your name
    description='A news recommendation system',  # Short description
    long_description=open('README.md').read(),   # Readme as long description
    long_description_content_type='text/markdown',
    url='https://github.com/rdsilva01/recomm',  # GitHub URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='==3.10.14',
)