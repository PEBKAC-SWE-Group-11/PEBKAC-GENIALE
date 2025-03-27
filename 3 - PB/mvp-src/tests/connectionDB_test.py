# import unittest
# from unittest.mock import patch, MagicMock
# import psycopg2
# import os
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from data_processing.connectionDB import getDBConnection

# class TestConnectionDB(unittest.TestCase):

#     @patch('psycopg2.connect')
#     def test_getDBConnection_success(self, mock_connect):
#         mock_connect.return_value = MagicMock()
#         connection = getDBConnection()
#         self.assertIsNotNone(connection)
#         mock_connect.assert_called_once()

#     @patch('psycopg2.connect', side_effect=psycopg2.OperationalError("Connection failed"))
#     @patch('time.sleep', return_value=None)
#     def test_getDBConnection_failure(self, mock_sleep, mock_connect):
#         with self.assertRaises(psycopg2.OperationalError):
#             getDBConnection()
#         self.assertEqual(mock_connect.call_count, 10)
#         self.assertEqual(mock_sleep.call_count, 9)

# if __name__ == '__main__':
#     unittest.main()