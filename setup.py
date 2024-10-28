from setuptools import setup, find_packages

setup(
    name='archv',            
    version='0.1.0',                       
    packages=find_packages(),              
    install_requires=[
        'requests',
        'beautifulsoup4',
        'clean-text',
        'spacy',
        'torch',
        'numpy',
        'transformers',
        'redis',
        'chunkipy',
        'text_to_speech',
        'pyttsx3',
    ],
    dependency_links=[
        'git+https://github.com/diogocorreia01/PublicNewsArchive@main#egg=PublicNewsArchive',
        'git+https://github.com/LIAAD/yake@master#egg=yake',
    ],
    author='rdsilva01',                    
    description='Preservation and Recommendation of Digital Newspapers Data',  
    long_description=open('README.md').read(),  
    long_description_content_type='text/markdown',
    url='https://github.com/rdsilva01/archv', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10.12',
)