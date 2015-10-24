#!/usr/bin/python

import unittest
import time
import random
from clevertap import CleverTap

CT_ACCOUNT_ID = "948-4KK-444Z"
CT_ACCOUNT_PASSCODE = "QAE-AWB-AAAL"

foods = ['pizza', 'burgers', 'sushi']
colors = ['blue', 'green', 'red', 'yellow']

class CleverTapTests(unittest.TestCase):
    def setUp(self):
        self.clevertap = CleverTap(CT_ACCOUNT_ID, CT_ACCOUNT_PASSCODE)

    def test_upload(self):
        data = [
                {"type":"event",
                    "Identity":"6264372123",
                    "ts":int(time.time()), 
                    "evtName":"choseNewFavoriteFood", 
                    "evtData":{
                        "value":random.choice(foods)
                        },
                    },

                {"type":"profile", 
                    "Identity":"6264372123",
                    "ts":int(time.time()), 
                    "profileData":{
                        "favoriteColor":random.choice(colors),
                        "Age":30,
                        "Phone":"+14155551234",
                        "Email":"peter@foo.com",
                        }, 
                    }
                ]

        res = self.clevertap.up(data) or {}
        self.assertEqual(res.get("processedRecords:", 0), 2, "%s records failed"%(len(res.get("unprocessedRecords:", data))))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(CleverTapTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
