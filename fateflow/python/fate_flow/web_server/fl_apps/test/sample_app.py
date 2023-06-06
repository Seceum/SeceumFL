import unittest, sys
sys.path.append("./")
import sample_app

class MyTestCase(unittest.TestCase):
    def sample_stats(self):
        sample_app.__sample_stats()
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()


