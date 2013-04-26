from lr.plugins.filters import ICustomFilterPolicy, ISchemaProvider
from pylons import config

import json, jsonschema, logging, os

log = logging.getLogger(__name__)


FILTER_ID = "lrmi-1.1"
SCHEMA_FILE = "lrmi.json"


class SchemaOrgFilterPolicy(ICustomFilterPolicy, ISchemaProvider):

    def __init__(self):
        super(SchemaOrgFilterPolicy, self).__init__()
        self.schema_obj = None
        self.validator = None

        path = os.path.dirname(__file__)
        self.schema_file = os.path.join(path, SCHEMA_FILE)

        self.filter_id =FILTER_ID
        self.filter_description = '''LRMI 1.1 using Schema.org 1.0a encoded into JSON formatted HTML Microdata.'''
        
        self.s_info = {
                "schema_id": self.filter_id,
                "description": self.filter_description,
                "content-type": "application/json; charset=utf-8"
        }


    def schema_ids(self):
        return [self.filter_id]


    def schema_info(self, schema_id=None): 
        if schema_id == self.filter_id:
            return self.s_info
        else:
            return None

    def schema(self, schema_id=None):
        info = self.schema_info(schema_id)
        if info is not None:
            try:
                data = {
                    "data": open(self.schema_file).read()
                }
                data.update(info)
                return data
            except:
                pass
        return None

    def activate(self):

        with open(self.schema_file) as f:
            self.schema_obj = json.load(f)

        self.validator = jsonschema.Draft4Validator(self.schema_obj, format_checker=jsonschema.FormatChecker())

        super(SchemaOrgFilterPolicy, self).activate()


    def name(self):
        return self.filter_id


    def filter(self, rd3=None):

        if self.validator != None and rd3["payload_placement"] == "inline":
            try:
                err_msg = ""
                errors = sorted(self.validator.iter_errors(rd3["resource_data"]), key=lambda e: e.path)
                for idx, err in enumerate(errors, 1):
                    err_msg += "{0}. {1}\n".format(idx, err)

                if err_msg != "":
                    return [True, err_msg]

            except Exception as e:
                return [True, e.message]


        return [False, None]



        