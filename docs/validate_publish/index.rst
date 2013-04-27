******************************
Filtered Validation On Publish
******************************

Overview
========

Included in this distribution of Learning Registry Node software, is some additional functionality that permits the publisher to validate their submission as JSON encoded HTML Microdata using LRMI 1.1 (Schema.org v1.0a) vocabulary.

When publishing using this optional service, if your submissions contains errors, returned will be a very detailed report on how your submission failed against the schema check.


Enabling Filtering During Publish
=================================

The process of enabling optional filtering during publish is a matter of adding one additional property, ``filter`` to the ``POST`` request.  The value of the ``filter`` property should be the name of the schema you wish to be checked.  To discover what filters are available on your node, refer to the `Schema Service API`_.


Publish Service API
-------------------

.. http:post:: /publish

        **Arguments:**

            None

        **Request Object:**

        .. sourcecode:: javascript

            {
                "documents": [ 
                                        // array of
                                        // resource data description documents

                    {resource_data_description} 
                                        // resource data to be published

                ],

                "filter": "string"      
                                        // name of filter to optional validate with

            }

        **Results Object:**

        .. sourcecode:: javascript

            {

                "OK": boolean,          
                                        // true if successful

                "error": "string",      
                                        // text describing global error
                                        // present only if NOT OK

                "document_results": [
                                        // array of per document results

                    {

                        "doc_ID": "string",            
                                        // ID of the document

                        "OK": boolean   
                                        // true if document was published

                        "error": "string"              
                                        // text describing error or filter failure
                                        // present only if NOT OK
                    }

                ]

            }

        :statuscode 200: no error
        :statuscode 500: error  


Discovering Available Filters
=============================

In order to make use of the filtering functionality during publish, you must know the name of the filter you wish to invoke.  To discover a new service has been added called Schema API.


Schema Service API
------------------

.. http:get:: /schema

    Returns a list of all available schema

    **Arguments:**

        None


    **Results Object:**

    .. sourcecode:: javascript


        {
            "OK": boolean,              // true if schemas exist, 
                                        // false if error or no schemas exist

            "error": "string",
                                        // text describing error,
                                        // present only if "OK" is false.

            "schemas": {                 
                                        // object containing key-value pairs which 
                                        // describe available schemas

                "key_id": {
                                        // "key_id" should be the string value identifier of
                                        // the available schema.

                    "schema_id":  "string",
                                        // same value as "key_id", string value identifier of
                                        // the schema
                    
                    "description": "string",
                                        // a short description of the what the schema validates

                    "content-type": "string",
                                        // the expected mime-type of the schema when requested
                                        // null if not downloadable.

                    "optional": boolean,
                                        // if this schema is available for optional invocation
                                        // true: available for optional invocation
                                        // false: not-available for optional invocation


                }


            }

        }

    :statuscode 200: no error



.. http:get:: /schema/(string:schema_id)

    Returns the the schema content specified by (`schema_id`). The Content-Type of the response is
    dependent upon the specified schema.

    :param schema_id: the "schema_id" property of the desired schema.
    :type schema_id: string

    :status 200: Success
    :status 404: requested schema not found.


    **Example Request**

    .. sourcecode:: http

        GET /schema/hello-world HTTP/1.1
        Host: example.com
        Accept: application/json


    **Example Response**

    .. sourcecode:: http

        HTTP/1.1 OK
        Content-Type: application/json; charset=utf-8

        {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "title": "hello world" 
            "properties": {
                "message": {
                    "enum": [ "hello world"]
                }
            }
        }



Adding Additional Filter Plugins
================================

Filters are implemented as `Yapsy plugins`_ that implement ``lr.plugins.ICustomFilterPolicy`` and ``lr.plugins.ISchemaProvider``.

.. py:module:: lr.plugins


.. py:class:: ICustomFilterPolicy

    Permits you to implement a custom policy filter on publish. ICustomFilterPolicy plugins is evaluated just before filters advertised within the Publish service document. You should also implement an ISchemaProvider if your plugin should be optional.
  
    .. py:method:: optional(self)
        
        Indicates of the filter is optional or must always be enabled. Default is True

    .. py:method:: name(self)
        
        This is the name of the filter that can be used to invoke when publishing

    .. py:method:: filter(self, rd3=None)
        
        This is the logic used when the filter is invoked.
        Return [ True, "Message" ] if filtering rd3. [ False, None ] otherwise.
    



.. py:class:: ISchemaProvider

    Should be implemented as a mixin to any other Learning Registry plugin. This will allow a schema to be discoverable on the `Schema Service API`_.

    .. py:method:: schema_ids(self)
        
        This is list of schema identifiers that are available for request

    .. py:method:: schema_info(self, schema_id=None)
        
        This information about a specific schema; "schema_id", "description", and "content-type", "optional".  If schema will not be available for download, "content-type" must be None.

        Returned Object:

        .. sourcecode:: json

            {
                "schema_id": "schema identifier",
                "description": "what the schema does",
                "content-type": "text/plain",
                "optional": True
            }


    .. py:method:: schema(self, schema_id=None)
        
        This returns the schema "data", "schema_id", "description", "optional", and "content-type" for the specified schema_id

        Returned Object:

        .. sourcecode:: json

            {
                "schema_id": "schema identifier",
                "description": "what the schema does",
                "content-type": "text/plain",
                "optional": True,
                "data": "Schema data as string"
            }

.. _Yapsy plugins: http://yapsy.sourceforge.net/
