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
    api_hostname = 'api.wzrkt.com'

    def __init__(self, account_id, account_passcode):
        self.account_id         = account_id
        self.account_passcode   = account_passcode
        self.req_id             = None
        self.url                = None

    def __repr__(self):
        return "%s(account_id=%s, passcode=%s)" % (self.__class__.__name__, self.account_id, self.account_passcode)


    @property
    def api_endpoint(self):
        return 'https://%s' % (self.__class__.api_hostname)


    def up(self, data):
        """upload an array of profile and/or event dicts"""

        # validate data
        validation_error = self._validate("up", data)

        if validation_error:
            raise Exception(validation_error)
            return 

        # construct the request url
        self.url = '/'.join([self.api_endpoint, "up"])

        # construct the request params
        payload = {"p":self.account_passcode, "d":data}
        # request args
        args = {"id":self.account_id, "payload":payload}

        # request headers
        headers_params = {'Content-Type':'application/x-www-form-urlencoded'}

        return self._call(args=args, headers_params=headers_params)


    def profiles(self, query, batch_size=10):
        """download profiles defined by query"""
        return self._fetch("profiles", query, batch_size=batch_size)


    def events(self, query, batch_size=10):
        """download events defined by query"""
        return self._fetch("events", query, batch_size=batch_size)


    def _fetch(self, type, query, batch_size=10):

        # create our records cache
        self.records = []

        # validate query
        validation_error = self._validate(type, query)

        if validation_error:
            raise Exception(validation_error)
            return

        # construct the request url
        self.baseurl = '/'.join([self.api_endpoint, "api/%s.json"%type])

        # add id, passcode and batch_size to the url as query args
        self.url = "%s?id=%s&p=%s&batch_size=%s"%(self.baseurl, self.account_id, self.account_passcode, batch_size)

        # the request body is the json encoded query
        body = json.dumps(query)

        # request headers
        headers_params = {'Content-Type':'application/json;charset=utf-8'}

        # make the request
        res = self._call(body=body, headers_params=headers_params) or {}

        # initial request is for the req_id
        self.req_id = res.get("CONTENT", {}).get("req_id", None)
        
        # if we have a req_id then make a second request with the req_id
        if self.req_id:
            # construct the request url
            # add id, passcode and req_id to the url as query args
            self.url = "%s?id=%s&p=%s&req_id=%s"%(self.baseurl, self.account_id, self.account_passcode, self.req_id)

            def call_records():
                # make the request
                res = self._call() or {}
                content = res.get("CONTENT", {})

                # add the new records array to our records array
                data = content.get("data", [])
                self.records += data

                # if the request returns a new req_id, update the url with the new req_id
                self.req_id = content.get("req_id", None)
                self.url = "%s?id=%s&p=%s&req_id=%s"%(self.baseurl, self.account_id, self.account_passcode, self.req_id)
                
            # keep making requests with the new req_id as long as we have a req_id 
            while True:
                call_records()

                if self.req_id == None:
                    break
                else:
                    call_records()

        return self.records


    def _call(self, **kwargs):

        # its always a POST request
        headers_params = kwargs.get('headers_params', {}) 
        args = urllib.urlencode(kwargs.get('args', {}))
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
            print e
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

        if type == "up":
            for record in data or []:

                Identity = record.get("Identity", None) or record.get("FBID", None) or record.get("GPID", None) or record.get("WZRK_G", None)
                if Identity is None:
                    validation_error = "record must contain an Identity, FBID, GPID or WZRK_G field: %s"%record
                    return validation_error
                    break

                ts = record.get("ts", None)
                if not isinstance(ts, (int, long)):
                    validation_error = "record must contain an unix epoch integer timestamp in a ts field: %s"%record
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

                    # validate some common profileData fields
                    Age = profileData.get("Age", None)
                    if Age and not isinstance(Age, int): 
                        validation_error = "profile Age must be an integer: %s"%record
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

        # TODO
        if type == "profiles":
            pass

        # TODO
        if type == "events":
            pass

        return validation_error

