import setuptools

VERSION = '0.1' 
DESCRIPTION = 'DeepVerse6G'
LONG_DESCRIPTION = 'DeepVerse 6G dataset generator library'

# Setting up
setuptools.setup(
        name="DeepVerse6G", 
        version=VERSION,
        author="Umut Demirhan, Ahmed Alkhateeb",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license_files = ('LICENSE.txt', ),
        install_requires=['numpy',
                          'scipy',
                          'tqdm'
                          ],
        
        keywords=['mmWave', 'MIMO', 'DeepVerse', 'python', 'Beta'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent"
        ],
        package_dir={"": "src"},
        packages=setuptools.find_packages(where="src"),
        url='https://deepmimo.net/'
)