import unittest
import json
import logging
import os

script_dir = os.getcwd()
log_file_path = os.path.join(script_dir, "library_log.log")

logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_valid_json(json_str):
    try:
        json_object = json.loads(json_str)
        logger.info("JSON syntax is valid.")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"JSON syntax is not valid. Error: {e}")
        logger.error(f"At line {e.lineno}, column {e.colno}")
        return False

def is_valid_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            json_str = file.read()
            return is_valid_json(json_str)
    except FileNotFoundError:
        logger.error("File not found.")
        return False
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return False

class TestJsonValidation(unittest.TestCase):
    def test_valid_json_file(self):
        file_path = os.path.join(script_dir, "invalid.json")
        result = is_valid_json_file(file_path)
        self.assertTrue(result, f"Validation failed for file: {file_path}")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


