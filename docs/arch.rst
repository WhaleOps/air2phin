Architecture
============

Airphin is a rule based AST transformer, using `LibCST <https://github.com/Instagram/LibCST>`_ to parse and transform Python code,
and Yaml file to define the transformation rules.

The main date flow as below:

.. image:: _static/how-it-work.png
  :width: 700
  :alt: data flow

And the steps of the transformation are:

- Get source content from file of stdin.
- Load all the rules from the Yaml file.
- Parse the source content into an LibCST.
- Transform the CST tree based on the rules.
- Provide the result to original file path with :code:`-airphin` as stem suffix or stdout.