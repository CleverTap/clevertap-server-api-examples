#!/usr/bin/python
import unittest
import time
import random
from clevertap import CleverTap

CT_ACCOUNT_ID = "W86-5K7-754Z"
CT_ACCOUNT_PASSCODE = "IYC-JWX-IPAL"

class CleverTapTargetTests(unittest.TestCase):
    def setUp(self):
        self.clevertap = CleverTap(CT_ACCOUNT_ID, CT_ACCOUNT_PASSCODE)

    def test_create(self):
        payload = {
                "name": "test2",
                "when": "now",
                "where": {
                    "event_name": "App Launched",
                    "from": 20160101,
                    "to": 20160313,
                    "common_profile_prop": {
                        "profile_fields": [
                            {
                                "name": "channels",
                                "value": ["bhome", "bhometest530a70c93b83286003f6bb5a"]
                                }
                            ]
                        }
                    },
                "content":{
                    "title":"Hello!",
                    "body":"Strictly Green Lantern fans only!",
                    "platform_specific": {
                        "ios": {
                            "deep_link": "judepereira.com",
                            "sound_file": "judepereira.wav",
                            "category": "reactive",
                            "badge_count": 1,
                            "foo": "bar_ios"
                            },
                        "android": {
                            "background_image": "http://judepereira.com/a.jpg",
                            "default_sound": True,
                            "deep_link": "judepereira.com",
                            "foo": "bar_android"
                            }
                        }
                    },
                "devices": [
                    "android",
                    "ios"
                    ],
                }

        res = self.clevertap.targets(self.clevertap.TargetActions.CREATE, payload) or {}
        print res
        status = res.get("status", None)
        self.assertEqual(status, "success", "create status is %s"%status)

    def test_estimate(self):
        payload = {
                "name": "green freedom",
                "when": "now",
                "where": {
                    "event_name": "App Launched",
                    "from": 20160101,
                    "to": 20160313,
                    },
                "content":{
                    "title":"Hello!",
                    "body":"Strictly Green Lantern fans only!",
                    "platform_specific": {
                        "ios": {
                            "deep_link": "judepereira.com",
                            "sound_file": "judepereira.wav",
                            "category": "reactive",
                            "badge_count": 1,
                            "foo": "bar_ios"
                            },
                        "android": {
                            "background_image": "http://judepereira.com/a.jpg",
                            "default_sound": True,
                            "deep_link": "judepereira.com",
                            "foo": "bar_android"
                            }
                        }
                    },
                "devices": [
                    "android",
                    "ios"
                    ],
                }

        res = self.clevertap.targets(self.clevertap.TargetActions.ESTIMATE, payload) or {}
        print res
        status = res.get("status", None)
        self.assertEqual(status, "success", "estimate status is %s"%status)

    def test_list(self):
        payload = {"from": 20160101, "to": 20160312} 
        res = self.clevertap.targets(self.clevertap.TargetActions.LIST, payload) or {}
        print res
        status = res.get("status", None)
        self.assertEqual(status, "success", "list status is %s"%status)

    def test_stop(self):
        payload = {"id": 1457737861} 
        res = self.clevertap.targets(self.clevertap.TargetActions.STOP, payload) or {}
        print res
        status = res.get("status", None)
        self.assertEqual(status, "success", "stop status is %s"%status)

    def test_result(self):
        payload = {"id": 1457744284} 
        res = self.clevertap.targets(self.clevertap.TargetActions.RESULT, payload) or {}
        print res
        status = res.get("status", None)
        self.assertEqual(status, "success", "result status is %s"%status)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(CleverTapTargetTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
