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


    def reset_url(self):
        self.url = None


    def up(self, data):

        # validate data
        validation_error = self._validate("up", data)

        if validation_error:
            raise Exception(validation_error)
            return 

        # construct the request url
        self.url = '/'.join([self.url or self.api_endpoint, "up"])

        # construct the request arguments
        payload = {"p":self.account_passcode, "d":data}
        args = {"id":self.account_id, "payload":payload}

        # request headers
        headers_params = {'Content-Type':'application/x-www-form-urlencoded'}

        return self._call(args=args, headers_params=headers_params)


    def profiles(self, query):

        # TODO

        # validate data
        validation_error = self._validate("profiles", query)

        if validation_error:
            raise Exception(validation_error)
            return

        # construct the request url
        self.url = '/'.join([self.url or self.api_endpoint, "profiles.json"])
        #return self._call(args=args, headers_params=headers_params)


    def events(self, query):

        # TODO

        # validate data
        validation_error = self._validate("events", query)

        if validation_error:
            raise Exception(validation_error)
            return

        # construct the request url
        self.url = '/'.join([self.url or self.api_endpoint, "events.json"])
        #return self._call(args=args, headers_params=headers_params)


    def _call(self, **kwargs):
        copy_of_url = self.url

        # reset self.url
        self.reset_url()

        # its always a POST request
        headers_params = kwargs.get('headers_params', None) 
        data = urllib.urlencode(kwargs.get('args', {}))

        # Create the request
        req = urllib2.Request(copy_of_url, data, headers_params)

        # Open the request
        f = urllib2.urlopen(req)

        # Get the response 
        response = f.read()

        # Close the opened request
        f.close()

        # Parse and return the response
        try:
            res = self._parse_response(response)
        except Exception, e:
            print e
            res = None

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

        if type == "profiles":
            pass

        if type == "events":
            pass

        return validation_error

    def _parse_response(self, response):
        """Parse a response from the API"""
        try:
            res = json.loads(response)
        except Exception, e:
            e.args += ('API response was: %s' % response)
            raise e

        return res
