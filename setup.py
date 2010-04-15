from setuptools import setup, find_packages


setup(
    name = 'hello-social-registration',
    version = __import__('social_registration').__version__,
    description = 'An extension to django-registration that adds backends for registration and authentication using Facebook and Twitter.',
    long_description = '',
    author = 'Bryan Veloso',
    author_email = 'bryan@revyver.com',
    url = 'http://github.com/revyver/hello-social-registration',
    download_url = '',
    license = 'BSD',
    packages = find_packages(exclude=['ez_setup']),
    include_package_data = True,
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

