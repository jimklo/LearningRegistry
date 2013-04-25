from lr.plugins.filters import ICustomFilterPolicy
from pylons import config

import json, jsonschema, logging, os

log = logging.getLogger(__name__)

class SchemaOrgFilterPolicy(ICustomFilterPolicy):

    def __init__(self):
        super(SchemaOrgFilterPolicy, self).__init__()

        self.schema = None
        self.validator = None

        path = os.path.dirname(__file__)
        self.schema_file = os.path.join(path, "lrmi.json")
        

    def activate(self):

        with open(self.schema_file) as f:
            self.schema = json.load(f)

        self.validator = jsonschema.Draft4Validator(self.schema, format_checker=jsonschema.FormatChecker())

        super(SchemaOrgFilterPolicy, self).activate()


    def schema(self):
        return self.schema_file

    def name(self):
        return "lrmi-1.1"


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

