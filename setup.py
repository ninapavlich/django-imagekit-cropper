from setuptools import setup, find_packages
#this is a test
setup(name = 'django-imagekit-cropper',
      description = 'Allow users to manually specify image variant crops',
      version = '0.3',
      url = 'https://github.com/ninapavlich/django-imagekit-cropper',
      author = 'Nina Pavlich',
      author_email='nina@ninalp.com',
      license = 'BSD',
      packages=find_packages(),
      package_data={'': ['*.py','*.css','*.js']},
      include_package_data=True,
      install_requires = ['setuptools', 'Django', 'django-grappelli', 'django-imagekit'],
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'License :: OSI Approved',
            'Operating System :: OS Independent',
            'Programming Language :: Python'
      ]
)
