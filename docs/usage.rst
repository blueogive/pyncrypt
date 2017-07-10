=====
Usage
=====

To use pyncrypt in a project:

.. code-block:: python

    import pyncrypt
    import dotenv
    import os


    main(**kwargs):
        msg = 'The password for {user} is {passwd}.'
        print(msg.format(user=username, passwd=vault.require(username)))


    if __name__ == '__main__':
        dotenv.load_dotenv(dotenv.find_dotenv())
        vault = KeyStore(os.environ['PASSPHRASE'])
        vault.require('my_user')  # Will prompt for password on first use
        main(username='my_user', vault=vault)


The project folder must also include an environment file—named ``.env``
by default—assiging a value to the ``PASSPHRASE`` environment variable
referenced in the script. [1]_


.. code-block:: shell

    # Environment variables go here, can be read by `python-dotenv` package:
    #
    # DO NOT ADD THIS FILE TO VERSION CONTROL!
    PASSPHRASE="This is my hard-to-guess passphrase!"


.. [1] Any valid shell variable name may be used; ``PASSPHRASE`` is offered
       as an example.
