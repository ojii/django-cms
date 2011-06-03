# -*- coding: utf-8 -*-
from django.core.handlers.wsgi import WSGIHandler
from django.core.management import call_command
from django.core.servers.basehttp import (WSGIServer, AdminMediaHandler, 
    WSGIRequestHandler, WSGIServerException)
from django.test.simple import dependency_ordered
from django.test.testcases import TestCase
from selenium import selenium
import socket
import threading

def create_test_db():
    from django.db import connections, DEFAULT_DB_ALIAS

    # First pass -- work out which databases actually need to be created,
    # and which ones are test mirrors or duplicate entries in DATABASES
    mirrored_aliases = {}
    test_databases = {}
    dependencies = {}
    for alias in connections:
        connection = connections[alias]
        if connection.settings_dict['TEST_MIRROR']:
            # If the database is marked as a test mirror, save
            # the alias.
            mirrored_aliases[alias] = connection.settings_dict['TEST_MIRROR']
        else:
            # Store a tuple with DB parameters that uniquely identify it.
            # If we have two aliases with the same values for that tuple,
            # we only need to create the test database once.
            item = test_databases.setdefault(
                connection.creation.test_db_signature(),
                (connection.settings_dict['NAME'], [])
            )
            item[1].append(alias)

            if 'TEST_DEPENDENCIES' in connection.settings_dict:
                dependencies[alias] = connection.settings_dict['TEST_DEPENDENCIES']
            else:
                if alias != DEFAULT_DB_ALIAS:
                    dependencies[alias] = connection.settings_dict.get('TEST_DEPENDENCIES', [DEFAULT_DB_ALIAS])

    # Second pass -- actually create the databases.
    old_names = []
    mirrors = []
    for signature, (db_name, aliases) in dependency_ordered(test_databases.items(), dependencies):
        # Actually create the database for the first connection
        connection = connections[aliases[0]]
        old_names.append((connection, db_name, True))
        test_db_name = connection.creation.create_test_db(1, autoclobber=True)
        for alias in aliases[1:]:
            connection = connections[alias]
            if db_name:
                old_names.append((connection, db_name, False))
                connection.settings_dict['NAME'] = test_db_name
            else:
                # If settings_dict['NAME'] isn't defined, we have a backend where
                # the name isn't important -- e.g., SQLite, which uses :memory:.
                # Force create the database instead of assuming it's a duplicate.
                old_names.append((connection, db_name, True))
                connection.creation.create_test_db(1, autoclobber=True)

    for alias, mirror_alias in mirrored_aliases.items():
        mirrors.append((alias, connections[alias].settings_dict['NAME']))
        connections[alias].settings_dict['NAME'] = connections[mirror_alias].settings_dict['NAME']

    return old_names, mirrors

class StoppableWSGIServer(WSGIServer):
    """ WSGIServer with short timout, so that server thread can stop this server. """ 
    
    def server_bind(self): 
        """ Sets timeout to 1 second. """ 
        WSGIServer.server_bind(self) 

     
    def get_request(self): 
        """ Checks for timeout when getting request. """ 
        try: 
            sock, address = self.socket.accept() 
            sock.settimeout(None) 
            return (sock, address) 
        except socket.timeout: 
            raise 


class TestServerThread(threading.Thread): 
    """ Thread for running a http server while tests are running. """ 
    def __init__(self, address, port): 
        self.address = address 
        self.port = port 
        self._stopevent = threading.Event() 
        self.started = threading.Event() 
        self.error = None 
        super(TestServerThread, self).__init__() 
 
    def run(self): 
        """ Sets up test server and database and loops over handling http requests. """ 
        try: 
            handler = AdminMediaHandler(WSGIHandler()) 
            server_address = (self.address, self.port) 
            httpd = StoppableWSGIServer(server_address, WSGIRequestHandler) 
            httpd.set_app(handler) 
            self.started.set() 
        except WSGIServerException, e: 
            # Use helpful error messages instead of ugly tracebacks. 
            self.error = e 
            self.started.set() 
            return 
         
        # Must do database stuff in this new thread if database in memory. 
        from django.conf import settings 
        if (settings.DATABASE_ENGINE == "sqlite3" 
            and (not settings.TEST_DATABASE_NAME or settings.TEST_DATABASE_NAME == ":memory:")): 
            create_test_db()
            # Import the fixture data into the test database. 
            if hasattr(self, 'fixtures'): 
                # We have to use this slightly awkward syntax due to the fact 
                # that we're using *args and **kwargs together. 
                call_command('loaddata', *self.fixtures, **{'verbosity': 0}) 
             
        # Loop until we get a stop event 
        while not self._stopevent.isSet(): 
            httpd.handle_request() 
         
    def join(self, timeout=None): 
        """ Stop the thread and wait for it to end. """ 
        self._stopevent.set() 
        threading.Thread.join(self, timeout) 


class SeleniumTestCase(TestCase):
    def start_test_server(self, address='localhost', port=8000): 
        """ 
        Creates a live test server object (instance of WSGIServer). 
        """ 
        self.server_thread = TestServerThread(address, port) 
        self.server_thread.start() 
        self.server_thread.started.wait() 
        if self.server_thread.error: 
            raise self.server_thread.error 
     
    def stop_test_server(self): 
        if self.server_thread: 
            self.server_thread.join()
            
    def setUp(self):
        self.start_test_server()
        self.selenium = selenium('localhost', 4444, '*firefox', 'http://127.0.0.1:8000')

    def tearDown(self):
        self.selenium.stop()
        self.stop_test_server()
