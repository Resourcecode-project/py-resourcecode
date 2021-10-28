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

.. code-block:: shell

   $ source env-resourcecode/bin/activate
   (env-resourcecode)$


Install the library
-------------------

In this virtual environment, you can now install the library. The library is not
available on PyPI yet, but on a private repository. Therefore, you need an
access token to install it. You can ask for a token access by writing an email
to `nicolas.raillard AT ifremer DOT fr` to get one.

Once you have an access token, you can install the library using the following
command :


.. code-block:: shell

   (env-resourcecode)$ python -m pip install resourcecode \
      --extra-index-url https://<username>:<your_personal_token>@gitlab.ifremer.fr/api/v4/projects/1881/packages/pypi/simple

where you need to replace `<your_personal_token>` by the token provided to you,
and <username> by your user name.  If the token is correct, the installation
will start.

To test whether the install has been successful, you can run:

.. code-block:: shell

   (env-resourcecode)$ python -c "import resourcecode ; print(resourcecode.__version__)"
   0.1.0

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
