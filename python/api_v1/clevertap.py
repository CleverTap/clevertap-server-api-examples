# -*- coding: utf-8 -*-

# Copyright 2015 CleverTap
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = ['CleverTap']

import json
import urllib
import urllib2

class CleverTap(object):
    api_hostname = 'api.clevertap.com'
    api_version = 1

    class TargetActions(object):
        CREATE = "create"
        ESTIMATE = "estimate"
        LIST = "list"
        RESULT = "result"
        STOP = "stop"

        @classmethod
        def valid_actions(cls):
            return [cls.CREATE, cls.ESTIMATE, cls.LIST, cls.RESULT, cls.STOP]

    def __init__(self, account_id, account_passcode):
        self.account_id         = account_id
        self.account_passcode   = account_passcode
        self.cursor             = None
        self.url                = None
        self.records            = []

    def __repr__(self):
        return "%s(account_id=%s, passcode=%s)" % (self.__class__.__name__, self.account_id, self.account_passcode)


    @property
    def api_endpoint(self):
        return 'https://%s/%s' % (self.__class__.api_hostname, self.__class__.api_version)


    def upload(self, data):
        """upload an array of profile and/or event dicts"""

        # validate data
        validation_error = self._validate("upload", data)

        if validation_error:
            raise Exception(validation_error)
            return 

        # construct the base request url
        self.url = '/'.join([self.api_endpoint, "upload"])

        # the request body is the json encoded data
        body = json.dumps({"d":data})

        # request headers
        headers_params = {'Content-Type':'application/json;charset=utf-8'}

        # make the request
        return self._call(body=body, headers_params=headers_params)

    def targets(self, action, payload):

        # validate 
        validation_error = self._validate(action, payload)

        if validation_error:
            raise Exception(validation_error)
            return

        url_action = None

        if action in self.TargetActions.valid_actions():
            url_action = action

        if not url_action:
            print "unknown targets action %s" % action
            return

        if url_action == self.TargetActions.ESTIMATE:
            payload['estimate_only'] = True
            url_action = self.TargetActions.CREATE

        # construct the request url
        self.url = '/'.join([self.api_endpoint, "targets", "%s.json"%url_action])

        # the request body is the json encoded payload
        body = json.dumps(payload) if payload else None

        # request headers
        headers_params = {'Content-Type':'application/json'}

        # make the request
        return self._call(body=body, headers_params=headers_params)

    def profile(self, email=None, identity=None, objectId=None):
        """fetch an individual user profile by ID, one of email, identity or CleverTap objectID"""

        if email is None and identity is None and objectId is None:
            raise Exception("profile requires one of email, identity or objectId")
            return

        # construct the request url
        self.url = '/'.join([self.api_endpoint, "profile.json"])

        if email is not None:
            self.url += "?email=%s" % email

        elif identity is not None:
            self.url += "?identity=%s" % identity

        elif objectId is not None:
            self.url += "?objectId=%s" % objectId

        # request headers
        headers_params = {'Content-Type':'application/json'}

        # make the request
        return self._call(headers_params=headers_params)

    def profiles(self, query, batch_size=10):
        """download profiles defined by query"""
        return self._fetch_records("profiles", query, batch_size=batch_size)


    def events(self, query, batch_size=10):
        """download events defined by query"""
        return self._fetch_records("events", query, batch_size=batch_size)


    def _fetch_records(self, type, query, batch_size=10):

        # reset our records cache
        self.records = []

        # validate query
        validation_error = self._validate(type, query)

        if validation_error:
            raise Exception(validation_error)
            return

        # construct the base request url
        self.baseurl = '/'.join([self.api_endpoint, "%s.json"%type])

        _args = urllib.urlencode({"query":json.dumps(query), 'batch_size':batch_size})
        # add query and batch_size as query args
        self.url = "%s?%s"%(self.baseurl, _args)

        # request headers
        headers_params = {'Content-Type':'application/json;charset=utf-8'}

        # make the request
        res = self._call(headers_params=headers_params) or {}

        # initial request is for the cursor
        self.cursor = res.get("cursor", None)
        
        # if we have a cursor then make a second request with the cursor
        if self.cursor:

            # construct the request url
            # add the cursor
            self.url = "%s?cursor=%s"%(self.baseurl, self.cursor)


            # convenience inner function to handle cursor requests 
            def call_records():
                # make the request
                res = self._call() or {}

                # parse response
                self.cursor = res.get("next_cursor", None)
                new_records = res.get("records", [])

                # add the new records array to our records array
                self.records += new_records

                # if the request returns a new cursor, update the api url with the new cursor
                if self.cursor:
                    self.url = "%s?cursor=%s"%(self.baseurl, self.cursor)
                else:
                    self.url = None
            

            # keep making requests with the new cursor as long as we have a cursor 
            while True:
                if self.cursor == None:
                    break
                else:
                    call_records()

        return self.records


    def _call(self, **kwargs):

        if self.url == None:
            print "api url is None"
            return None

        headers_params = kwargs.get('headers_params', {}) 
        # add account_id, and passcode to request headers 
        headers_params['X-CleverTap-Account-Id'] = self.account_id
        headers_params['X-CleverTap-Passcode'] = self.account_passcode
        
        args = kwargs.get("args", None)
        if args:
            args = urllib.urlencode(args)

        body = kwargs.get("body", None)

        # Create the request
        req = urllib2.Request(self.url, args, headers_params)

        if body:
            req.add_data(body)

        try:
            # Open the request
            f = urllib2.urlopen(req)
            # Get the response 
            response = f.read()
            # Close the opened request
            f.close()

        except Exception, e:
            print "%s: %s" % (e, e.read())
            return None

        # Parse and return the response
        try:
            res = self._parse_response(response)
        except Exception, e:
            print e
            res = None

        return res
            
    def _parse_response(self, response):
        """Parse a response from the API"""
        try:
            res = json.loads(response)
        except Exception, e:
            e.args += ('API response was: %s' % response)
            raise e

        return res

    def _validate(self, type, data):
        """Simple data validation"""
        validation_error = None

        if not self.account_id:
            validation_error = "clevertap account id missing"
            return validation_error

        if not self.account_passcode:
            validation_error = "clevertap account passcode missing"
            return validation_error

        if type in [self.TargetActions.CREATE, self.TargetActions.ESTIMATE]:
            if data is None:
                return "Push targets action %s requires a payload"%type

            if (data.get("name", None) is None):
                return "Push targets action %s requires a name"%type

            if (data.get("where", None) is None) and (data.get("segment", None) is None):
                return "Push targets action %s requires a where or segment value"%type

            if (data.get("where", None) is not None) and (data.get("segment", None) is not None):
                return "Push targets action %s does not support both a where value and a segment value, specify one or the other"%type

            if (data.get("segment", None) is not None):
                if data.get("segment") != "all":
                    return "Push targets action %s segment value must be 'all'"%type

            if (data.get("content", None) is None):
                return "Push targets action %s requires a content dict"%type

            if (data.get("content", None) is not None):
                if (data.get("content", {}).get("title", None) is None) or (data.get("content", {}).get("body", None) is None): 
                    return "Push targets action %s content dict requires a title and a body"%type

            if (data.get("devices", None) is None):
                return "Push targets action %s requires a devices array"%type

            return validation_error

        if type == self.TargetActions.LIST:
            # no-op
            return validation_error

        if type in [self.TargetActions.RESULT, self.TargetActions.STOP]:
            if (data is None) or (data.get("id", None) is None):
                validation_error = "Push targets %s action requires a target id"%type

            return validation_error

        if type == "upload":
            for record in data or []:

                identity = record.get("identity", None) or record.get("FBID", None) or record.get("GPID", None) or record.get("objectId", None)
                if identity is None:
                    validation_error = "record must contain an identity, FBID, GPID or objectId field: %s"%record
                    return validation_error
                    break

                record_type = record.get("type", None)
                if record_type not in ['profile', 'event']:
                    validation_error = "record type must be profile or event: %s"%record
                    return validation_error
                    break

                if record_type == "profile":
                    profileData = record.get("profileData", None)
                    if profileData is None or not isinstance(profileData, dict): 
                        validation_error = "record with type profile must contain a profileData dict: %s"%record
                        return validation_error
                        break

                    Phone = profileData.get("Phone", None)
                    if Phone and (not isinstance(Phone, str) or not Phone.startswith("+")): 
                        validation_error = "profile Phone must be a string and start with +<country code>: %s"%record
                        return validation_error
                        break

                if record_type == "event":
                    evtData = record.get("evtData", None)
                    if evtData is None or not isinstance(evtData, dict): 
                        validation_error = "record with type event must contain an evtData dict: %s"%record
                        return validation_error
                        break

        return validation_error

