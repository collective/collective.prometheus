============================
Prometheus Plone Integration
============================

This package publishes Plone statistics in a format that can be consumed by Prometheus_.

It was largely based on ``munin.zope``. See https://pypi.org/project/munin.zope/

It provides the following data:

  * The number of running Zope ZServer threads (with the `zserver` extra)
  * The number of Zope ZServer threads not in use (with the `zserver` extra)
  * The number of objects in the Zope database
  * Memory used by the Zope cache
  * The number of objects that can be stored in the Zope cache
  * ZODB load count
  * ZODB store count
  * ZODB connections
  * Active Zope Objects
  * Total Zope Objects

Installation (using Buildout)
-----------------------------

Add ``collective.prometheus`` to your instance eggs in ``buildout.cfg``.

Usage
-----

Assuming Plone listens on ``localhost:8000``, start your Plone instance and visit http://localhost:8000/@@metrics to see the output and confirm that data is being reported.

If so, add a job to your ``scrape_configs`` in ``pometheus.yaml``:

.. code-block:: yaml

    - job_name: 'plone'
      metrics_path: '/@@metrics'
      static_configs:
      - targets: ['localhost:8000']

.. _Prometheus: https://prometheus.io/
