"""Test related functionality

Adds a Pylons plugin to `nose
<http://www.somethingaboutorange.com/mrl/projects/nose/>`_ adds some
command switches to control remote testing.

"""
import os
import sys
import nose
from urlparse import urlsplit
from nose.plugins import Plugin

relay = None

class Relay(object):
    node = None
    node_parts = None
    couchdb = None
    couch_parts = None

class PylonsRelayPlugin(Plugin):
    """Nose plugin extension

    For use with nose to allow a project to be configured before nose
    proceeds to scan the project for doc tests and unit tests. This
    prevents modules from being loaded without a configured Pylons
    environment.

    """
    def __init__(self):
      Plugin.__init__(self)
      self.enabled = False
      self.remoteRelay = 'node_relay'
      self.remoteRelayUser = 'node_relay_user'
      self.remoteRelayPass = 'node_relay_pass'
      self.remoteCouch = 'couchdb_relay'
      self.remoteCouchUser = 'couchdb_relay_user'
      self.remoteCouchPass = 'couchdb_relay_pass'

      self.name = 'relay'

      self.remote = Relay()

    def add_options(self, parser, env=os.environ):
        """Add command-line options for this plugin"""
        Plugin.options(self, parser, env)

        parser.add_option("--with-node-%s" % self.name,
                          dest=self.remoteRelay, type="string",
                          default=None,
                          help="Relay tests to different Pylons instance")


        parser.add_option("--with-couchdb-%s" % self.name,
                          dest=self.remoteCouch, type="string",
                          default=None,
                          help="Relay tests to different CouchDB instance")


    def configure(self, options, conf):
        """Configure the plugin"""
        if hasattr(options, self.remoteRelay) and getattr(options, self.remoteRelay):
            self.remote.node = getattr(options, self.remoteRelay)
            if self.remote.node:
                self.enabled = True
                self.remote.node_parts = urlsplit(self.remote.node)

            if hasattr(options, self.remoteCouch) and getattr(options, self.remoteCouch):
                self.remote.couchdb = getattr(options, self.remoteCouch)

                if self.remote.couchdb:
                  self.remote.couchdb_parts = urlsplit(self.remote.couchdb)


    def begin(self):
        """Called before any tests are collected or run

        Loads the application, and in turn its configuration.

        """
        global relay
        import pdb; pdb.set_trace()
        if self.enabled:
            relay = self.remote


if __name__ == "__main__":
    nose.main(addplugins=[PylonsRelayPlugin()])

