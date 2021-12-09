import json
from os import name
import typing as t
from flask import request
from marshmallow import Schema, fields
from marshmallow.decorators import post_dump, post_load
from flask_jsonpify import jsonpify


class EntityType: 
    def __init__(self, name: str, id: str)-> None:
        self.id = id
        self.name = name
        self.properties = []

class Property: 
    def __init__(self, id, name) -> None:
        self.id = id
        self.name = name

class PropertySchema(Schema):
    id = fields.Str()
    name = fields.Str()
    
class EntityTypeSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    properties = fields.Nested(PropertySchema, many=True)
    

class ServiceProperty:
    def __init__(self, service_url, service_path) -> None:
        self.service_url = service_url
        self.service_path = service_path

class ServicePropertySchema(Schema):
    service_url = fields.Url()
    service_path = fields.Str()
    
    '''
    Per request, map the host name of the request to the service url, remove the leading slash
    '''
    @post_dump
    def add_host_service_url(self, data, many):
        result = {}
        for k, v in data.items() :
            result[k] = v
            if k == "service_url" :
                result[k] = request.host_url+v[1:]
                
        return result
    
class ExtendService: 
    def __init__(self, service_url, service_path="/propose_properties") -> None:
        self.propose_properties = ServiceProperty(service_url, service_path)

class ExtendServiceSchema(Schema):
    propose_properties = fields.Nested(ServicePropertySchema())
    

class ViewService:
    def __init__(self, service_url, service_path="/view/{{id}}") -> None:
        self.url = "{}{}".format(service_url,service_path)
        
class ViewServiceSchema(Schema):
    url = fields.Url()
    @post_dump
    def set_view_url(self, data, many):
        return {"url" : request.host_url+data["url"][1:] }

class PreviewService:
    def __init__(self, service_url, service_path="/preview/{{id}}", width=200, height=200) -> None:
        self.url = "{}{}".format(service_url, service_path)
        self.width = width
        self.height =height

class PreviewServiceSchema(Schema):
    url = fields.Url()
    width = fields.Int()
    height = fields.Int()
    @post_dump
    def set_view_url(self, data, many):
        print(data)
        return {"url" : request.host_url+data["url"][1:],
                "width": data["width"],
                "height" : data["height"]}

class ReconcileRequest:
    def __init__(self, query=None, queries=None, extend=None) -> None:
        self.query = query
        self.queries = queries
        self.extend = extend

class ReconcileRequestSchema(Schema):
    query = fields.Str()
    queries = fields.Dict()
    extend = fields.Dict()
    
    @post_load
    def make_reconcilie_request(self, data, **kwargs):
        print(data)
        return ReconcileRequest(**data)
    

class ReconcileService: 
    def __init__(self, name, version, base_path="/reconcile") -> None:
        self.name = name
        self.version = str(version)
        self.manifest = Manifest(self.name, [self.version])
        self.services = {}
        self.base_path = base_path
        self.entities = {}
        
    def extend(self, func, *args) ->t.Callable:
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
        self.services["extend"] = func
        self.manifest.extend = ExtendService(self.base_path)
        def inner() -> t.Callable:
            return func()
            
        return inner
    
    def search(self, func, *args) ->t.Callable:
        """
        @rs.search
        def my_search(reconcile: ReconcileRequest)
        
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
        """
        self.services["search"] = func
        def inner() -> t.Callable:
            return func()
            
        return inner        
    
    def search_batch(self, func, *args) ->t.Callable:
        '''
        @rs.search_batch
        def search_batch(reconcile: ReconcileRequest = None):

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
        self.services["search_batch"] = func
        def inner() -> t.Callable:
            return func()
            
        return inner
    
    def view(self, func, *args) -> t.Callable:
        self.services["view"] = func
        self.manifest.view = ViewService(self.base_path)
                
        def inner() -> t.Callable:
            return func()
        return inner

    def preview_wh(self, width, height): 
        '''
        @rs.preview_wh(200, 200)
        
        def preview_item(id):

        This funtion is called when a matched results are hovered over in OpenRefine
        Openrefine creates an iframe of size width x height where you can display summary data for the entity
        Arg: 
            id - the entity id

        Return : 
            HTML 

        '''

        
        self.manifest.preview = PreviewService(self.base_path, "/preview/{{id}}", width, height)
        def preview(func, *args) -> t.Callable:
        
            self.services["preview"] = func        
            def inner() -> t.Callable:
                return func()
            return inner
        return preview

    def add_entity(self, entity: EntityType) -> None: 
        id = entity.id
        self.entities[id] = entity

    # this is not a good way to do this
    # meta props should be tied to a type or to the result
    def get_props_meta(self, props) : 
        p_meta = []
        p_ids = list(map(lambda x : x["id"], props))
        for k,e in self.entities.items() : 
            print(e)
            for p in e.properties : 
                if p.id in p_ids : 
                    p_meta.append({"id": p.id, "name": p.name})
                    
        return p_meta
    

    def serve(self, path, id):
        
        if path == "propose_properties" :
            if "extend" not in self.services :
                raise InvalidUsage("extend is not enabled for this API")
            
            type = request.args.get("type") 
            if type is None :
                raise InvalidUsage("Missing type parameter for Entity")
            
            # should I raise this? types seem loosely coupled 
            #if type not in self.entities :
            #    raise InvalidUsage("Supplies type parameter is not available")
            print(self.entities)
            schema = EntityTypeSchema().dump(self.entities[type])
            return jsonpify(schema)
        
        if path == "view" :
            return self.services["view"](id)
        
        if path == "preview" : 
            return self.services["preview"](id)
        
        if request.method == "POST" : 
            incoming_request = ""
            if request.mimetype in ['application/json', 'application/javascript'] :
                incoming_request = request.get_json()
            else :
                incoming_request = request.form
            
            #####
            ## convert str to dict
            ###
            ir = {}
            if "query" in incoming_request :
                ir = incoming_request
            else :
                for k in incoming_request.keys(): 
                    ir[k] = json.loads(incoming_request[k])
            
            print(ir)

            reconcile_request = ReconcileRequestSchema().load(ir)
            if reconcile_request.query is not None:
                result = self.services["search"](reconcile_request)
            
            if reconcile_request.queries is not None: 
                result = self.services["search_batch"](reconcile_request)
            
            if reconcile_request.extend is not None: 
                result = self.services["extend"](reconcile_request)
                requested_properties = reconcile_request.extend["properties"]
                print(requested_properties)
                result["meta"] = self.get_props_meta(requested_properties)
        

            return jsonpify(result)

        
        return jsonpify(ManifestSchema().dump(self.manifest))
        
    
class Manifest:
    def __init__(self, name, versions) -> None:
        """
        Create a manifest to describe the service
        Args:
            name str: Contain the name of the service
            versions list: list of strings for versions            
                        e.g. 
                                ["1.1", "1.2", "1.2.1", "2.3"]
        
        """
        self.versions = versions
        self.name = name
        self.defaultTypes = []
        self.identifierSpace = None
        self.schemaSpace = None
        self.view = None
        self.preview = None
        self.suggest = None
        self.extend = None
    
    def add_type(self, type: EntityType) -> None: 
        self.defaultTypes[type.id] = type
        
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class ManifestSchema(Schema) :
    versions = fields.List(fields.Str()) 
    name = fields.Str()
    defaultTypes = fields.Nested(EntityTypeSchema, many=True)
    identifierSpace = fields.Url()
    schemaSpace = fields.Url()
    view = fields.Nested(ViewServiceSchema())
    preview = fields.Nested(PreviewServiceSchema())
    suggest = None  # TODO: Create a Suggest service
    extend = fields.Nested(ExtendServiceSchema()) 
    SKIP_VALUES = [None]

    @post_dump
    def remove_skip_values(self, data, many):
        
        return {
            key: value for key, value in data.items()
            if value not in self.SKIP_VALUES
        }

class InvalidUsage(Exception):
    status_code = 400
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
