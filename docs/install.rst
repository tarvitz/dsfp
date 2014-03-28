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

Python 3.3
``````````
document build requirements stored in py3.txt

.. code-block:: bash

   user@localhost$ virtualenv --no-site-packages venv3
   user@localhost$ source venv3/bin/activate
   user@localhost$ pip install -r requirements/py3.txt

Dependencies
------------
* python 2.7+
* python 3.3+


Tests
~~~~~
You could run tests via `python -m unittest module` or via `run_tests.sh` script

.. code-block:: bash

   user@localhost$ ./run_tests.sh dsfp.tests.TestDSFPReader


Usage
~~~~~
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



that's all folks