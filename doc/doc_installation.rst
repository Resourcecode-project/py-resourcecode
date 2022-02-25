How to install the library ?
============================

Create a dedicated virtual environment
--------------------------------------

To install the library, you may first of all, create a dedicated virtual
environment:

.. code-block:: shell

   $ cd /your/work/directory
   $ python3 -m venv env-resourcecode

then, you activate it:

On Unix-based OS:

.. code-block:: shell

   $ source env-resourcecode/bin/activate
   (env-resourcecode)$

On windows:

.. code-block:: shell

   <Your_PATH>.\env-resourcecode\Script\activate
   (env-resourcecode)<Your_PATH>

Install the library
-------------------

In this virtual environment, you can now install the library. The library is 
available on PyPI, and installation is straightfoward, using the following
command :


.. code-block:: shell

   (env-resourcecode)$ python -m pip install resourcecode


To test whether the install has been successful, you can run:

.. code-block:: shell

   (env-resourcecode)$ python -c "import resourcecode ; print(resourcecode.__version__)"
   0.5.4

which should print the current locally installed version of `resourcecode`.


Known issues
------------

During the `pip install` step, you may have an error say

   Could not install packages due to an EnvironmentError: 404 Client Error: Not
   Found for url: https://pypi.org/simple/resourcecode/


this is a known issue, which occurs with `pip <= 19.0`. To overcome this issue,
you simply have to update `pip` to it latest version:

.. code-block:: shell

   (env-resourcecode)$ python -m pip install --upgrade pip

and re-run the install step which should be fine.

At this time, `python >= 3.10` is not supported.
