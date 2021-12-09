# Reconciliation 
Reconciliation is a python flask framework that works with OpenRefine Reconcile Data capabilities.
Reconcile is the ability to match and enhance data from multiple sources over the web.

This framework provides the ability to create one of those sources without having to reimplement the underlying protocol.
Reconciliation will provide

* Request parsing
* Handler for Reconciliation JSON Protocol
* Function decorators for
  * Search
    * Required
    * Used to map incoming data to an entity id in your data
  * Search in batch mode
    * Required
    * Same as search but used for batches for performance
  * Extend 
    * Optional - but kind of useless without it
    * Used to add additional columns / fields to end users data
  * Preview
    * Optional - really handy for users
    * Used as a hover preview method, by creating an iframe in openrefine
  * View
    * Optional - really useful
    * Used to show the entity in a browser

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
'''
def extend(reconcile: ReconcileRequest):

This is the request that handles performing "Add column based on reconciled data"
A list of properties and a list of entity ids are passed in 
The entity and the value of the propery are expected as results.

reconcile.extend.ids contains the list of entity ids
reconcile.extend.properties contains the list of properties expected

Return expected

{
    "rows" : {
                <entity_id> : {
                    "<property_id>" : [ { "<str>" : "<property value>"}],
                    "<property_id2>" : [ { "<str>" : "<property value>"},{ "<str>" : "<property other value>"}]
                    .....
                    

                },
                 <entity_id2> : {
                    "<property_id>" : [ { "<str>" : "<property value>"}],
                    "<property_id2>" : [ { "<str>" : "<property value>"},{ "<str>" : "<property other value>"}]
                    .....
                    

                },
                .......

    }
}

'''
@rs.preview_wh(width, height) # in pixels
'''
def preview_item(id):

This funtion is called when a matched results are hovered over in OpenRefine
Openrefine creates an iframe of size width x height where you can display summary data for the entity
Arg: 
    id - the entity id

Return : 
    HTML 

'''



@rs.view
'''
def view_item(id):

This function is called in openrefine when a user clicks a matched entity 
You can return html, redirect, a file download, anything that is browser compatible 

Arg: 
    id = the entity id

Return: 
    Browser compatible content 

'''

```
# Reconciliation Example
Start by checking out openrefine at https://openrefine.org/ and downloading the latest version of the OpenRefine software
The example provided solves a simple problem, you have a spreadsheet of The Guardian's 2010 Greatest Movies of all time, 
however it's mising the movies posters. 
This sample app will load a spreadsheet call movie_posters.xlsx which contains some of the movie posters.

First start this app, assume you've cloned the [reconciliation github repo](https://github.com/preftech/reconciliation), setup your [virtualenv](https://sourabhbajaj.com/mac-setup/Python/virtualenv.html) or [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) for python

### Step 1
```
pip install -r requirements.txt
python app.py
```
This should start the reconciliation service at http://127.0.0.1:5000/reconcile/

### Step 2
Next launch OpenRefine and create a new project with the guardian_2010_greatest_films_of_all_time.csv
![Create New Project](https://github.com/preftech/reconciliation/blob/main/docs/images/create_new.png?raw=true)

Select next > Create Project (defaults on this page are fine)
You should have a spreadsheet page with the list of movies

### Step 3
Next step lets reconcile the movie titles against our reconciliation service.
Click the dropdown menu next to "title" > Reconcile > Start Reconciling
![Start Reconciling](https://github.com/preftech/reconciliation/blob/main/docs/images/start_reconciling.png?raw=true)

Next Add the reconcilation service, you will see an >Add Standard Service button on the bottom left
Type in http://127.0.0.1:5000/reconcile/ **Ensure you include the trailing slash**
> Add Service

![Add Service](https://github.com/preftech/reconciliation/blob/main/docs/images/add_service.png?raw=true)

Again the defaults should be fine here.
Under the covers this calls http://127.0.0.1:5000/reconcile/ and receives back a list of services you have enabled
This services are linked to the EntityType you added to ReconcileService and @rs.* decorators in your code.
```
et = EntityType("Movie", "/movie")
et.properties.append(Property("imdb", "IMDB URL"))
et.properties.append(Property("poster", "Poster URL"))
```

```
@rs.view
.....
````







## Attributions
A thanks has to go out to the following for data used in the example 
* Babu Thomas (@babu-thomas)
  * MovieLens project
  * https://github.com/babu-thomas/movielens-posters
* Owen Temples - https://www.linkedin.com/in/owentemple
  * Guardian's 2010 Greatest Movies of all Time 
  * https://data.world/owentemple/greatest-films-of-all-time