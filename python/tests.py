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
                    "Identity":"6264372124",
                    "ts":int(time.time()), 
                    "evtName":"choseNewFavoriteFood", 
                    "evtData":{
                        "value":random.choice(foods)
                        },
                    },

                {"type":"profile", 
                    "Identity":"6264372124",
                    "ts":int(time.time()), 
                    "profileData":{
                        "favoriteColor":random.choice(colors),
                        "Age":30,
                        "Phone":"+14155551234",
                        "Email":"peter@foo.com",
                        }, 
                    },

                {"type":"event",
                  "FBID":"34322423",
                  "ts":int(time.time()),
                  "evtName":"Product viewed",
                  "evtData":{
                    "Product name":"Casio Chronograph Watch",
                    "Category":"Mens Watch",
                    "Price":59.99,
                    "Currency":"USD"
                    },
                  },

                {"type":"event",
                  "Identity":"jack@gmail.com",
                  "ts":int(time.time()),
                  "evtName":"Charged",
                  "evtData":{
                    "Amount":300,
                    "Currency":"USD",
                    "Payment mode":"Credit Card",
                    "Items":[
                      {
                        "Category":"books",
                        "Book name":"The millionaire next door",
                        "Quantity":1
                        },
                      {
                        "Category":"books",
                        "Book name":"Achieving inner zen",
                        "Quantity":4
                        }
                      ]
                    },
                  },
                ]

        res = self.clevertap.up(data) or {}
        self.assertEqual(res.get("processedRecords:", 0), 4, "%s records failed"%(len(res.get("unprocessedRecords:", data))))

    def test_download_events(self):
        query = {"event_name": 
                "choseNewFavoriteFood",
                "from": 20150810,
                "to": 20151025
                }

        res = self.clevertap.events(query)
        self.assertTrue( len(res) > 0 )

    def test_download_profiles(self):
        query = {"event_name":
                "choseNewFavoriteFood",
                "from": 20150810,
                "to": 20151025
                }

        res = self.clevertap.profiles(query)
        self.assertTrue( len(res) > 0 )

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(CleverTapTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
