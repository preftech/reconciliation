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

With OpenRefine you have an out of the box you have a UI and tool that will allow individuals or teams to work without having to build a tool from scratch. 
![OpenRefine Screen Shot](https://raw.githubusercontent.com/preftech/reconciliation/main/docs/images/refine.png)


# Installation
Install using pip
```sh
pip install reconciliation
```

# Usage
This is a flask based app that allows you to control how you route, authenticate, log etc.. A full example exists in the app.py file

```python
from reconcile import EntityType, InvalidUsage, Property, ReconcileRequest, ReconcileService

# Create a flask app
app = Flask(__name__)

# initialize a ReconcileService
rs = ReconcileService("Movie Reconciliation", "0.1a")

# Create an entity you want to serve 
et = EntityType("Movie", "/movie")
et.properties.append(Property("imdb", "IMDB URL"))
et.properties.append(Property("poster", "Poster URL"))
# Add the entity to the service
rs.add_entity(et)

# Set the entrypoint for your application
# This lets you control the URLs and if you wish to put a URL key for authentication you can do so here
@app.route("/reconcile/", methods=['GET', 'POST'])
@app.route("/reconcile/<path:path>", methods=['GET', 'POST'])
@app.route("/reconcile/<path:path>/<path:id>", methods=['GET', 'POST'])
def handle(path=None, id=None) :
    return rs.serve(path, id)

```

The following decorators are used to handle incoming requests
```python

@rs.search
def my_search(reconcile: ReconcileRequest)
    '''
    Will be called with a single search query
    reconcile.query will contain a string for the entity being searched for
    expects a return of :
        { "result" : [
                        {
                        "id": <unique id of entity>,
                        "name": <name of entity>, 
                        "score": <int of a score>,
                        "match": <True or False>, # Return True for exact match.
                        "type":     [
                                        { # EntityType, ideally as added to the rs above
                                            "id": et.id,
                                            "name": et.name
                                        }
                                    ]
                        }              
                    ]
        }
    '''

@rs.search_batch
def my_search_batch(reconcile: ReconcileRequest):
    '''
    By Default OpenRefine will attempt to batch up queries
    These will be available in reconcile.queries as a dictionary queries key off a query id
    e.g. 
        {
            <query_id_1> : {"query" : "text to search for"} ,
            <query_id_2> : {"query" : "something else to search for"}
            ......
        }

    The expected return is
    {"results" : {
                    <query_id_1> : { "result" : .... } # same as single search result
                    <query_id_2> : { "result" : .....}
                    ......
                }
    }
    '''

@rs.extend
@rs.preview_wh
@rs.view

```
# Reconciliation Example
Provided 


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

## Attributions
A thanks has to go out to the following for data used in the example 
* Babu Thomas 
  * MovieLens project
  * https://github.com/babu-thomas/movielens-posters
* Owen Temples 
  * Guardian's 2010 Greatest Movies of all Time 
  * https://data.world/owentemple/greatest-films-of-all-time