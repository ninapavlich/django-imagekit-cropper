from setuptools import setup, find_packages

setup(
    name = 'django-imagekit-cropper',
    version = '1.15',
    author = 'Nina Pavlich',
    author_email='nina@ninalp.com',
    url = 'https://github.com/ninapavlich/django-imagekit-cropper',
    license = "MIT",
    description = 'Allow users to manually specify image variant crops',
    keywords = ['libraries', 'web development', 'cms', 'django', 'django-grappelli'],
    include_package_data = True,
    packages = ['imagekit_cropper'],
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)
