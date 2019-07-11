import unittest
from cptch_net.client import CptchNet
from config import API_KEY

class MainAttributesTest(unittest.TestCase):

    validKey = API_KEY #enter your API key
    invalidKey = '112312312313'
    invalidKeyType = 123
    emptyKey = ''

    def setUp(self):
        self.client = CptchNet

    def tearDown(self):
        del self.client

    def test_with_invalid_keys(self):
        with self.assertRaises(Exception) as context:
            self.client(self.invalidKeyType)
        self.assertTrue(type(context.exception) is AssertionError, msg='Problem with Exception for invalid key')
        self.assertEqual(len(self.client(self.emptyKey).getKey()), False, msg='Invalid Empty key is not empty')

    def test_with_valid_key_type(self):
        client = self.client(self.validKey)
        self.assertEqual(type(client.getKey()), str, msg='Problem with Exception for valid key' )


class SettersTest(unittest.TestCase):
    pass

class GettersTest(unittest.TestCase):
    pass

class ResolveTest(unittest.TestCase):
    pass



if __name__ == "__main__":
    unittest.main()