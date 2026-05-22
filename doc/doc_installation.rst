How to install the library ?
============================

Create a dedicated virtual environment
--------------------------------------

To install the library, you may first of all, create a dedicated virtual
environment with a python version at least `3.11`:

.. code-block:: shell

   $ cd /your/work/directory
   $ python3 -m venv env-resourcecode

then, you activate it:

On Unix-based OS:

.. code-block:: shell

   $ source env-resourcecode/bin/activate
   (env-resourcecode)$

On windows:

.. code-block:: batch

   Your_PATH>.\env-resourcecode\Scripts\activate
   (env-resourcecode) Your_PATH:\> 

Install the library
-------------------

In this virtual environment, you can now install the library. The library is 
available on PyPI, and installation is straightforward, using the following
command :


.. code-block:: shell

   (env-resourcecode)$ python -m pip install resourcecode


To test whether the install has been successful, you can run:

.. code-block:: shell

   (env-resourcecode)$ python -c "import resourcecode ; print(resourcecode.__version__)"

which should print the current locally installed version of `resourcecode`.

Alternative installation with uv
--------------------------------

For a faster and more reliable installation, you can use `uv <https://docs.astral.sh/uv/>`_,
a modern Python package installer:

.. code-block:: shell

   $ uv venv env-resourcecode --python 3.11
   $ source env-resourcecode/bin/activate
   (env-resourcecode)$ uv pip install resourcecode

For development, you can also use uv to sync all dependencies:

.. code-block:: shell

   $ uv sync --all-extras --dev
   $ uv run pytest
