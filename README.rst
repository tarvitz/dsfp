DarkSouls Save File Parser
==========================
.. _badges:

.. image:: https://travis-ci.org/tarvitz/dsfp.svg?branch=master
    :target: https://travis-ci.org/tarvitz/dsfp

.. image:: https://badge.fury.io/py/dsfp.svg
  :target: http://badge.fury.io/py/dsfp

.. image:: https://pypip.in/implementation/dsfp/badge.svg
    :target: https://pypi.python.org/pypi/dsfp/
    :alt: Supported Python implementations
  
.. image:: https://pypip.in/license/dsfp/badge.svg
  :target: https://pypi.python.org/pypi/dsfp/
  :alt: License

.. image:: https://pypip.in/status/dsfp/badge.svg
    :target: https://pypi.python.org/pypi/dsfp/
    :alt: Development Status

* DSFP means Darksouls Save File Parser.
* `Dark Souls <http://darksouls.wikia.com/wiki/Dark_Souls>`_ is game of
  Namco Bandai with pretty hard to get it finished without being killed.
  Lot's of death, fun and broken gamepads/keyboards.

**DSFP** *serves* for getting/fetching your saved characters statistics purposes.

.. contents:: :local:
    :depth: 2

Original source
~~~~~~~~~~~~~~~

Original source and some key knowledge were taken from this
`gist <https://gist.github.com/infausto/8382836/>`_.

Common features
~~~~~~~~~~~~~~~
Supports fetching data about character's death, his/her general stats, hp and stamina.
Whole bunch of reversed stats you can see in datasheet document which is placed
`here <docs/datasheet.rst>`_

(*Help for reverse engineering DarkSouls save file is appreciated*).

Binary Templates
~~~~~~~~~~~~~~~~
Since May 02 2015 I use binary templates for further save format investigations
and to make reverse engineering work much easier. Common documentation that
have been written in 2014 has some wrong information about different places.
Use `010editor <http://www.sweetscape.com/010editor/>`_ to process Dark Souls
save file with given templates.

Installation
~~~~~~~~~~~~
For general installation you would probably need virtual environment with pip
installed:

Python 2.7
``````````
.. code-block:: bash

   user@localhost$ virtualenv --no-site-packages venv
   user@localhost$ source venv/bin/activate
   user@localhost$ pip install -r requirements/base.txt

*optional*

.. code-block:: bash

   user@localhost$ pip install -r requirements/docs.txt

Python 3.x
``````````
document build requirements stored in py3.txt

.. code-block:: bash
   user@localhost$ virtualenv --no-site-packages venv3
   user@localhost$ source venv3/bin/activate
   user@localhost$ pip install -r requirements/py3.txt

Dependencies
------------
* python 2.7
* python 3.3
* python 3.4


Tests
~~~~~
Simply run ``python setup.py test`` or
You could run tests via `python -m unittest module` or via `run_tests.sh` script

.. code-block:: bash

   user@localhost$ ./run_tests.sh tests.TestDSFPReader

Fast Usage
~~~~~~~~~~
You can parse Dark Souls save files and get data in standard python
dictionary format

.. code-block:: python

    >>> import dsfp
    >>> ds = dsfp.DSSaveFileParser('saves/DRAKS0005.sl2')
    >>> data = ds.get_stats()
    >>> data
    [{
        'attunement': 8, 'body': 0, 'class': 0, 'color': 0, 'deaths': 0,
        'dexterity': 13, 'earned': 60, 'endurance': 12, 'face': 0, 'faith': 9,
        'gift': 0, 'hairs': 0, 'hp': 594, 'hp2': 594, 'hp_current': 594,
        'humanity': 0, 'intelligence': 9, 'level': 4,
        'male': False,  # False means female
        'name': u'TEST_2', 'resistance': 11, 'souls': 60, 'stamina': 95,
        'stamina2': 95, 'stamina3': 95, 'strength': 13,
        'time': 62, # in seconds
        'vitality': 11
       }]




Datasheets
~~~~~~~~~~
There's no many information about Dark Souls save file format (as well as the
other games), so there's not much complete around its format.
Some knowledge represented `here <docs/datasheet.rst>`_.

Please notify me here or by email (tarvitz [at] blacklibrary.ru)
if you have something interesting around whole file format.

Documentation
~~~~~~~~~~~~~
Whole bunch of the docs you can read by clicking this link
`dsfp.readthedocs.org <http://dsfp.readthedocs.org>`_


Development
~~~~~~~~~~~

.. note::

    Huge buch of data now represented in datasheets are still not covered in
    dsfp "api" just cause whole file-format and its datasheet is the main priority.
    You can use it for build your own parser or just read some non-random data
    from *.sl2 files.
    Though dsfp is not complete as it should, please search/read information in
    the docs mentioned above.

Roadmap
~~~~~~~
I have no certain roadmap for this project and I inspect the data whenever I want
to do it. In general these moments could be very short/long from time to time. So don't
expect me finishing this work to some certain moment or something clear enough.

Use ``./scripts/watcher.py`` and the other scripts (or may be another methods) to inspect
data you need, contact me if you want to share them and have fun ;).

Watching
~~~~~~~~
Use ``scripts/spy.py`` for watching some blocks of data (could be slow for present moment)

.. code-block:: bash

  (ve)tarvitz@mebook dsfp $ python ./scripts/spy.py -f remote/draks0005.sl2 -w json/watch.json
  modified: 0 [01:41:29]
  0x000002c0[       704] 1571248212 0x5da75854    <- 3092053692 0xb84cfebc
  0x000002c4[       708] 1935086728 0x73571488    <- 1146802795 0x445ad26b
  0x000002c8[       712] 3053911314 0xb606fd12    <- 1220380586 0x48bd87aa
  0x000002cc[       716]  904361964 0x35e777ec    <- 2331046835 0x8af0f3b3
