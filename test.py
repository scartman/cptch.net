import unittest
from client import CptchNet

class CptchTest(unittest.TestCase):

    validKey = '' #enter your API key
    invalidKey = '123123123123'
    invalidKeyType = 123

    def setUp(self):
        self.client = CptchNet

    def test_with_invalid__key_type(self):
        with self.assertRaises(Exception) as context:
            self.client(self.invalidKeyType)
        self.assertTrue(type(context.exception) is AssertionError, msg='Problem with Exception for invalid key')

    def test_with_valid_key_type(self):
        client = self.client(self.validKey)
        self.assertEqual(type(client.key), str, msg='Problem with Exception for valid key' )

    def test_function_getBalance_with_valid_key(self):
        client = self.client(self.validKey)
        self.assertEqual(type(client.getBalance()), float, msg='Balance is not a float type')

    def test_function_getBalance_with_invalid_key(self):
        with self.assertRaises(Exception) as context:
            self.client(self.invalidKey).getBalance()
        self.assertTrue(type(context.exception) is AssertionError, msg='Problem with Exception for invalid key')

if __name__ == "__main__":
    unittest.main()