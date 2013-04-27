from lr.tests import *
from lr.plugins import LRPluginManager, ISchemaProvider
import unittest, jsonschema, json, uuid


def has_schema_plugin(schema_name=None):
    if schema_name is not None:
        for plugin in LRPluginManager.getAllPlugins(ISchemaProvider):
            if plugin.name() == schema_name:
                return True
    return False

SCHEMA_NAME = "lrmi-1.1"

invalid_schema_request = {
    "properties": {
        "message": { "type": "string" },
        "OK": { "enum": [ False ] }
    },
    "required": ["message", "OK"]
}

valid_service = {
    "properties": {
        "OK": {
            "enum": [ True, False ]
        },
        "schemas": {
            "patternProperties": {
                ".*": {
                    "properties": {
                        "schema_id": { "type": "string" },
                        "description": { "type": "string" },
                        "content-type": { "type": ["string", "null"] },
                        "optional": { "type": "boolean" }

                    },
                    "required": [ "schema_id", "description", "content-type", "optional" ]
                }
            },
            "minProperties": 1
        },
        "error": {
            "type": "string"
        }
    },
    "required": [ "OK" ],
    "dependencies": {
        "OK": {
            "oneOf": [
                {
                    "required": [ "error", "OK" ],
                    "properties": {
                        "OK" : { "enum": [ False ]}
                    }
                },
                {
                    "required": [ "schemas", "OK" ],
                    "properties": {
                        "OK" : { "enum": [ True ]}
                    }
                }
            ]   
        }
    }
}

@unittest.skipUnless(has_schema_plugin(SCHEMA_NAME), "Plugin with ISchemaProvider for '%s' not installed." % SCHEMA_NAME)
class TestSchemaController(TestController):

    def test_index(self):
        response = self.app.get('/schema')

        obj = response.json
        
        # print "\n%s\n" % json.dumps(valid_service, indent=4)

        try:
            jsonschema.validate(obj, valid_service)
        except jsonschema.ValidationError:
            self.fail("Unexpected response format")

        assert "OK" in obj and obj["OK"] is True, "Missing OK = True"
        assert SCHEMA_NAME in obj["schemas"] and obj["schemas"][SCHEMA_NAME] is not None, "missing '%s' schema information" % SCHEMA_NAME


    def test_show(self):

        response = self.app.get('/schema/lrmi-1.1')
        assert "$schema" in response.json, "'%s' schema not properly returned." % SCHEMA_NAME


    def test_non_existent_show(self):

        response = self.app.get('/schema/%s' % str(uuid.uuid4()), expect_errors=True)

        assert response.status_code == 404, "Schema should not exist"

        try:
            jsonschema.validate(response.json, invalid_schema_request)
        except jsonschema.ValidationError:
            self.fail("Unexpected response format")




