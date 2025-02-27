import setuptools

VERSION = '0.0.4' 
DESCRIPTION = 'DeepVerse 6G'
LONG_DESCRIPTION = 'DeepVerse 6G dataset generator library'

# Setting up
setuptools.setup(
        name="DeepVerse", 
        version=VERSION,
        author="Umut Demirhan, Abdelrahman Taha, Shuaifeng Jiang, Ahmed Alkhateeb",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license_files = ('LICENSE.txt', ),
        install_requires=['numpy',
                          'scipy',
                          'tqdm',
                          'matplotlib',
                          'pyyaml',
                          'natsort',
                          'pandas'],
        
        keywords=['mmWave', 'MIMO', 'digital twin', 'wireless', 'python', 'Beta'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent"
        ],
        package_dir={"": "src"},
        packages=setuptools.find_packages(where="src"),
        url='https://deepverse6g.net/'
)