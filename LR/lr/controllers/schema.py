import logging, json

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from lr.plugins import LRPluginManager, ISchemaProvider
from lr.lib.base import BaseController, render

log = logging.getLogger(__name__)

class SchemaController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('schema', 'schemas')

    def index(self):
        """GET /schemas: All items in the collection"""
        # url('schemas')
        schemas = { "schemas": { } }
        for plugin in LRPluginManager.getAllPlugins(ISchemaProvider):
            plugin_sids = plugin.schema_ids()
            for sid in plugin_sids:
                schemas["schemas"].update({
                    sid: plugin.schema_info(sid)
                    })



        response.headers["Content-Type"] = "application/json; charset=utf-8"

        if len(schemas.keys()) == 0:
            schemas.update({
                'OK': False,
                'error': "No schemas available"
                })
        else:
            schemas.update({
                'OK': True
                })

        return json.dumps(schemas)    


    def show(self, id, format='json'):
        """GET /schemas/id: Show a specific item"""
        # url('schema', id=ID)
        # for some reason it can get mangled
        id = request.path.split("/")[-1]

        for plugin in LRPluginManager.getAllPlugins(ISchemaProvider):
            try:
                schema = plugin.schema(id)
                if schema is not None and schema["data"] is not None:
                    try:
                        response.headers["Content-Type"] = schema["content-type"]
                    except:
                        response.headers["Content-Type"] = "application/octet-stream"

                    return schema["data"]
            except:
                pass

        abort(404, 'Requested schema "{0}" not found.'.format(id), headers={"Content-Type": "application/json"})
                
