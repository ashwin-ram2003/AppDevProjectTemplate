
import unittest
from unittest.mock import MagicMock
from server.hardwareDatabase import (
    createHardwareSet,
    queryHardwareSet,
    updateAvailability,
    requestSpace,
)


class TestHardwareInventory(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        self.collection = self.client["HardwareCheckout"]["HardwareSets"]

    def test_create_hardware(self):
        self.collection.find_one.return_value = None

        result = createHardwareSet(self.client, "Arduino", 10)

        self.assertEqual(result["hwName"], "Arduino")
        self.assertEqual(result["capacity"], 10)
        self.assertEqual(result["availability"], 10)
        self.collection.insert_one.assert_called_once()

    def test_negative_capacity(self):
        with self.assertRaises(ValueError):
            createHardwareSet(self.client, "Arduino", -5)

    def test_duplicate_hardware(self):
        self.collection.find_one.return_value = {"hwName": "Arduino"}

        with self.assertRaises(ValueError):
            createHardwareSet(self.client, "Arduino", 10)

    def test_checkout_reduces_inventory(self):
        self.collection.update_one.return_value.matched_count = 1
        self.collection.find_one.return_value = {
            "hwName": "Arduino",
            "capacity": 10,
            "availability": 6,
        }

        result = requestSpace(self.client, "Arduino", 4)

        self.assertEqual(result["availability"], 6)
        self.collection.update_one.assert_called_once_with(
            {"hwName": "Arduino", "availability": {"$gte": 4}},
            {"$inc": {"availability": -4}},
        )

    def test_insufficient_inventory(self):
        self.collection.update_one.return_value.matched_count = 0

        with self.assertRaises(ValueError):
            requestSpace(self.client, "Arduino", 20)

    def test_zero_checkout(self):
        with self.assertRaises(ValueError):
            requestSpace(self.client, "Arduino", 0)

    def test_negative_checkout(self):
        with self.assertRaises(ValueError):
            requestSpace(self.client, "Arduino", -3)

    def test_availability_exceeds_capacity(self):
        self.collection.update_one.return_value.matched_count = 0

        with self.assertRaises(ValueError):
            updateAvailability(self.client, "Arduino", 15)


if __name__ == "__main__":
    unittest.main()
