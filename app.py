from flask import Flask, json, request, redirect
from pprint import pprint as pp
from flask_jsonpify import jsonify
import pandas as pd
from reconcile import EntityType, InvalidUsage, Property, ReconcileRequest, ReconcileService

app = Flask(__name__)

et = EntityType("Movie", "/movie")
et.properties.append(Property("imdb", "IMDB URL"))
et.properties.append(Property("poster", "Poster URL"))

rs = ReconcileService("Movie Reconciliation", "0.1a")
rs.add_entity(et)

@app.route("/reconcile")    # optional - forces a 301 redirect
@app.route("/reconcile/", methods=['GET', 'POST'])
@app.route("/reconcile/<path:path>", methods=['GET', 'POST'])
@app.route("/reconcile/<path:path>/<path:id>", methods=['GET', 'POST'])
def handle(path=None, id=None) :
    return rs.serve(path, id)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@rs.search
def search_single(reconcile: ReconcileRequest = None):
    
    # Single query
    return search(reconcile.query)
    
@rs.search_batch
def search_batch(reconcile: ReconcileRequest = None):
    # Batch of queries
    results = {}
    for k,v in reconcile.queries.items() : 
        q_txt = v["query"]
        results[k] = search(q_txt) 
    return results

@rs.extend
def extend(reconcile: ReconcileRequest = None):
    # Extend query
    # Contains document ids and properties to add
    # Response requires
    #   meta : [ properties ]
    #   rows : [ results ]
    result = {}
    extend = reconcile.extend
    ids = extend["ids"]
    props_requested = extend["properties"]
    if len(props_requested) > 0 :
        pr = list(map(lambda x: x["id"], props_requested))
    if ids is not None : 
        ids = list(map(lambda x: int(x), ids))
        result["rows"] =  get_by_id_props(ids, pr)
    
    return result

@rs.view    
def view_item(id):
    url = get_by_id(id, "imdb")
    #print(id)
    #print(url)
    return redirect(url)

@rs.preview_wh(200, 200)
def preview_item(id):
    html = """
    <html>
    <body><img src="{}" width="180", height="180"/>
    </body>
    </html>
    """
    poster = get_by_id(id, "poster")
    return html.format(poster)

###
#   Read an excel file which holds our sample data
#
##
df = pd.read_excel("movie_posters.xlsx", engine="openpyxl")


# Search excel file
def search(query):
    results = []
    # Find a movie by the title from movie_posters.xlsx
    match_results = df[df["title"].str.contains(query, na=False)]
    num_res = len(match_results)
    
    # Create Results
    for index, row in match_results.iterrows():
        score = (100 / num_res)
            
        match = {
            "id": row["id"],
            "name": row["title"], 
            "score": score,
            "match": (query in row.values and score == 100), # Return True for exact match.
            "type":     [{ 
                            "id": et.id,
                            "name": et.name
                          }
                         ]
            }
    
        results.append(match)
        
    return {"result": results}


# Extend data with additional properties 
def get_by_id_props(ids, props) :
    results_df = df[df["id"].isin(ids)]
    results = {}
    for idx, row in results_df.iterrows() :
        result_p = {}
        for p in props : 
            result_p[p] = [ {"str" :row[p]}]
        results[row["id"]] = result_p
    pp(results_df)
    return results
        

def get_by_id(id, column) :
    
    # Important to ensure that your excel and parameters are the cast to the same type
    # either int or str
    
    result_df = df[df["id"] == int(id)]
    for idx, row in result_df.iterrows() :
        #print(row)
        return str(row[column])