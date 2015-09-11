from setuptools import setup, find_packages

setup(
    name = 'django-imagekit-cropper',
    packages = ['django_imagekit_cropper'],
    version = '1.8',
    description = 'Allow users to manually specify image variant crops',
    author = 'Nina Pavlich',
    author_email='nina@ninalp.com',
    url = 'https://github.com/ninapavlich/django-imagekit-cropper',
    keywords = ['libraries', 'web development', 'cms', 'django', 'django-grappelli'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)