# Reconciliation 
Reconciliation is a python flask framework that works with OpenRefine Reconcile Data capabilities.
Reconcile is the ability to match and enhance data from multiple sources over the web.

This framework provides the ability to create one of those sources without having to reimplement the underlying protocol.
Reconciliation will provide

* Request parsing
* Handler for Reconciliation JSON Protocol
* Function decorators for
  * Search
  * Search in batch mode
  * Extend 
  * Preview
  * View

## Why use Open Refines reconciliation
OpenRefine provides a desktop/browser tool for data management and curation. This tool provides an excel like interface for cleaning, scripting abilities to augment data, enhancing data with the ability to fetch data over the internet and supliment the data you already have.
Details on how to use OpenRefine's Reconciliation interface are available https://docs.openrefine.org/manual/reconciling
A list of known publically available services is available https://reconciliation-api.github.io/testbench/


reconcile
    -> search

discover properties
    -> type

reconcile -> ids + properties 


query
querys
extend
    ids
    properties

# Data Attributions
A thanks has to go out to the following for data used in the example 
* Babu Thomas MovieLens project https://github.com/babu-thomas/movielens-posters
* Owen Temples Guardian's 2010 Greatest Movies of all Tim https://data.world/owentemple/greatest-films-of-all-time