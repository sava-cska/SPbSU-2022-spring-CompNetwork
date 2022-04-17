import unittest
from checksum.checksum import count_checksum, check_checksum

class CountChecksumTest(unittest.TestCase):
    def test_1(self):
        self.assertEqual(count_checksum(bytearray([1, 2, 3, 4])), (1 << 16) - (1 << 10) - (1 << 9) - 3)
    
    def test_2(self):
        self.assertEqual(count_checksum(bytearray([1, 2, 3])), (1 << 16) - (1 << 9) - 3)

class CheckChecksumTest(unittest.TestCase):
    def test_1(self):
        self.assertTrue(check_checksum(bytearray([1, 2, 3, 4]), (1 << 16) - (1 << 10) - (1 << 9) - 3))
    
    def test_2(self):
        self.assertFalse(check_checksum(bytearray([1, 2, 3]), (1 << 16) - (1 << 9) - 2))

if __name__ == '__main__':
    unittest.main()

