import unittest
from bot import check_pick


class TestEverything(unittest.TestCase):

    def test_pick_true(self):
        x = check_pick('Grand Abolisher')
        self.assertEqual(x, True)

    def test_pick_false(self):
        x = check_pick('Grand Tester')
        self.assertEqual(x, False)


if __name__ == '__main__':
    unittest.main()
