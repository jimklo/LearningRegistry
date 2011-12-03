"""Test related functionality

Adds a Pylons plugin to `nose
<http://www.somethingaboutorange.com/mrl/projects/nose/>`_ adds some
command switches to control remote testing.

"""
import os
import sys
import nose
from nose.plugins import Plugin

relay = None

class Relay(object):
    node = None
    node_user = None
    node_pass = None
    couchdb = None
    couchdb_user = None
    couchdb_pass = None

class PylonsRelayPlugin(Plugin):
    """Nose plugin extension

    For use with nose to allow a project to be configured before nose
    proceeds to scan the project for doc tests and unit tests. This
    prevents modules from being loaded without a configured Pylons
    environment.

    """
    enabled = False
    remoteRelay = 'node_relay'
    remoteRelayUser = 'node_relay_user'
    remoteRelayPass = 'node_relay_pass'
    remoteCouch = 'couchdb_relay'
    remoteCouchUser = 'couchdb_relay_user'
    remoteCouchPass = 'couchdb_relay_pass'

    name = 'relay'

    remote = Relay()

    def options(self, parser, env=os.environ):
        """Add command-line options for this plugin"""

        parser.add_option("--with-node-%s" % self.name,
                          dest=self.remoteRelay, type="string",
                          default=None,
                          help="Relay tests to different Pylons instance")

        parser.add_option("--with-node-user",
                          dest=self.remoteRelayUser, type="string",
                          default=None,
                          help="Basic Auth user for relay.")
        
        parser.add_option("--with-node-pass",
                          dest=self.remoteRelayPass, type="string",
                          default=None,
                          help="Basic Auth password for relay.")

        parser.add_option("--with-couchdb-%s" % self.name,
                          dest=self.remoteCouch, type="string",
                          default=None,
                          help="Relay tests to different CouchDB instance")

        parser.add_option("--with-couchdb-user",
                          dest=self.remoteCouchUser, type="string",
                          default=None,
                          help="Basic Auth user for CouchDB instance.")
        
        parser.add_option("--with-couchdb-pass",
                          dest=self.remoteCouchPass, type="string",
                          default=None,
                          help="Basic Auth password CouchDB instance.")


    def configure(self, options, conf):
        """Configure the plugin"""

        if hasattr(options, self.remoteRelay):
            remote.node = getattr(options, self.remoteRelay)
            if remote.node:
                self.enabled = True

            if hasattr(options, self.remoteRelayUser) and hasattr(options, self.remoteRelayPass):
                remote.node_user = getattr(options, self.remoteRelayUser)
                remote.node_pass = getattr(options, self.remoteRelayPass)
        
            if hasattr(options, self.remoteCouch):
                remote.couchdb = getattr(options, self.remoteCouch)

                if hasattr(options, self.remoteCouchUser) and hasattr(options, self.remoteCouchPass):
                    remote.couchdb_user = getattr(options, self.remoteCouchUser)
                    remote.couchdb_pass = getattr(options, self.remoteCouchPass)


    def begin(self):
        """Called before any tests are collected or run

        Loads the application, and in turn its configuration.

        """
        global relay

        if self.enabled:
            relay = self.remote


if __name__ == "__main__":
    nose.main(addplugins=[PylonsRelayPlugin()])

