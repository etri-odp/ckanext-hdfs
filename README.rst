.. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.

.. .. image:: https://travis-ci.org/etri-sodas/ckanext-hdfs.svg?branch=master
    :target: https://travis-ci.org/etri-sodas/ckanext-hdfs

.. .. image:: https://coveralls.io/repos/etri-sodas/ckanext-hdfs/badge.svg
  :target: https://coveralls.io/r/etri-sodas/ckanext-hdfs

.. .. image:: https://pypip.in/download/ckanext-hdfs/badge.svg
    :target: https://pypi.python.org/pypi/etri-sodas/ckanext-hdfs/
    :alt: Downloads

.. .. image:: https://pypip.in/version/ckanext-hdfs/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-hdfs/
    :alt: Latest Version

.. .. image:: https://pypip.in/py_versions/ckanext-hdfs/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-hdfs/
    :alt: Supported Python versions

.. .. image:: https://pypip.in/status/ckanext-hdfs/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-hdfs/
    :alt: Development Status

.. .. image:: https://pypip.in/license/ckanext-hdfs/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-hdfs/
    :alt: License

===========================================================
ckanext-hdfs - HDFS storing extension
===========================================================

.. Put a description of your extension here:
   What does it do? What features does it have?
   Consider including some screenshots or embedding a video!

ckanext-hdfs is an extension for enabling the file storage in HDFS - Hadoop Distributed File System.

This extension provides an ability to let users store a certain resource in HDFS, instead of the local file system.

Notes:

* JAVA_HOME and HADOOP_HOME needed to be set correctly.

------------
Requirements
------------

This extension was developed and tested under CKAN-2.7.3 and HADOOP-3.0.0

------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-hdfs:

1. Activate your CKAN virtual environment, for example::

    . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-hdfs Python package into your virtual environment::

    pip install ckanext-hdfs

3. Add ``hdfs`` setting in your CKAN config file (by default the config file is located at ``/etc/ckan/default/production.ini``) as follows.
    
    ckan.plugins = hdfs <other-plugins>
    ckan.hdfs.storage_path = /ckan/data

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

    sudo service apache2 reload


------------------------
Development Installation
------------------------

To install ckanext-hdfs for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/etri-odp/ckanext-hdfs.git
    cd ckanext-hdfs
    python setup.py develop
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.hdfs --cover-inclusive --cover-erase --cover-tests


----------------------------------------------
Registering ckanext-hdfs on PyPI
----------------------------------------------

ckanext-hdfs should be available on PyPI as
https://pypi.python.org/pypi/ckanext-hdfs. If that link doesn't work, then
you can register the project on PyPI for the first time by following these
steps:

1. Create a source distribution of the project::

     python setup.py sdist

2. Register the project::

     python setup.py register

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the first release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.1 then do::

       git tag 0.0.1
       git push --tags

================
Acknowledgements
================

This work was supported by Institute for Information & communications Technology Promotion (IITP) grant funded by the Korea government (MSIT) (No.2017-00253, Development of an Advanced Open Data Distribution Platform based on International Standards)
