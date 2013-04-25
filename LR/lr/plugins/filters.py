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


    def schema(self):
        '''This is the schema file that is used to filter data. Default is None.'''

        return None

    def filter(self, rd3=None):
        '''This is the logic used when the filter is invoked.
           Return [ True, "Message" ] if filtering rd3. [ False, None ] otherwise.'''

        raise NotImplementedError("filter function must be implemented")


ICustomFilterPolicy.ID = "Filter Policy"