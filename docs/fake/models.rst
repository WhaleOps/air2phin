fake.models
===========

Some fake for :code:`airlfow.models` about get object from database.

variable
--------

For :code:`airlfow.models.Variable` and return what we pass to it.

.. code-block:: python

    from air2phin.models import Variable
    
    var = Variable.get("var")
    print(var)
    # var
