from lr.plugins.base import BasePlugin

class ICustomFilterPolicy(BasePlugin):
    def __init__(self):
        super(ICustomFilterPolicy, self).__init__()


    def optional(self):
        '''Indicates of the filter is optional or must always be enabled. Default is True'''
        return True

    def name(self):
        '''This is the name of the filter that can be used to invoke when publishing'''

        raise NotImplementedError("name function must be implemented")


    def filter(self, rd3=None):
        '''This is the logic used when the filter is invoked.
           Return [ True, "Message" ] if filtering rd3. [ False, None ] otherwise.'''

        raise NotImplementedError("filter function must be implemented")


ICustomFilterPolicy.ID = "Filter Policy"


class ISchemaProvider(object):

    def __init__(self):
        super(ISchemaProvider, self).__init__()

    def schema_ids(self):
        '''This is list of schema identifiers that are available for request'''

        return []

    def schema_info(self, schema_id=None):
        '''This information about a specific schema; "schema_id", "description", and "content-type".'''

        return {
            "schema_id": str(schema_id),
            "description": "Not Available",
            "content-type": None,
            "optional": False
        }


    def schema(self, schema_id=None):
        '''This returns the schema "data", "schema_id", "description", and "content-type" for the specified schema_id'''

        data = self.schema_info(schema_id)
        data.update({
            "data": None
        })
        return data