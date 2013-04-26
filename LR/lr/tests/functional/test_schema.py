from lr.tests import *
from lr.plugins import LRPluginManager, ISchemaProvider
import unittest


def has_schema_plugin(schema_name=None):
    if schema_name is not None:
        for plugin in LRPluginManager.getAllPlugins(ISchemaProvider):
            if plugin.name() == schema_name:
                return True
    return False

SCHEMA_NAME = "lrmi-1.1"

@unittest.skipUnless(has_schema_plugin(SCHEMA_NAME), "Plugin with ISchemaProvider for '%s' not installed." % SCHEMA_NAME)
class TestSchemaController(TestController):

    def test_index(self):
        response = self.app.get('/schema')

        obj = response.json
        assert "OK" in obj and obj["OK"] is True, "Missing OK = True"
        assert SCHEMA_NAME in obj and obj[SCHEMA_NAME] is not None, "missing '%s' schema information" % SCHEMA_NAME


    def test_show(self):

        response = self.app.get('/schema/lrmi-1.1')
        assert "$schema" in response.json, "'%s' schema not properly returned." % SCHEMA_NAME