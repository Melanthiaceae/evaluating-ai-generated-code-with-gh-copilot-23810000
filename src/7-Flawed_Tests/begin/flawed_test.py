"""Shipping quote calculator with a test suite.

Run the tests with:

    python flawed_test.py

The store advertises free shipping for orders of $50 or more. 
The regular shipping cost for orders under $50 is $6.99. 
The shipping_cost function calculates the shipping cost accordingly.
"""
import unittest

FREE_SHIPPING_THRESHOLD = 50.00
STANDARD_SHIPPING_COST = 6.99

def shipping_cost(order_total):
	"""Return the shipping charge for an order total in dollars."""
	if order_total >= FREE_SHIPPING_THRESHOLD:
		return 0.00
	return STANDARD_SHIPPING_COST

def order_summary(items):
	"""Return the item subtotal and shipping charge for ``(name, price)`` pairs."""
	subtotal = sum(price for _, price in items)
	return {
		"subtotal": subtotal,
		"shipping": shipping_cost(subtotal),
		"total": subtotal + shipping_cost(subtotal),
	}


class ShippingQuoteTests(unittest.TestCase):
	def test_small_order_pays_standard_shipping(self):
		quote = order_summary([("notebook", 12.00), ("pens", 8.00)])
		
		self.assertEqual(quote["subtotal"], 20.00)
		self.assertEqual(quote["shipping"], STANDARD_SHIPPING_COST)

	def test_large_order_gets_free_shipping(self):
		quote = order_summary([("backpack", 65.00)])
		
		self.assertEqual(quote["shipping"], 0.00)

	def test_threshold_order_gets_free_shipping(self):
		quote = order_summary([("headphones", 50.00)])
		
		self.assertEqual(quote["shipping"], 0.00)

	def test_total_includes_shipping_for_a_small_order(self):
		quote = order_summary([("water bottle", 15.00)])

		self.assertAlmostEqual(quote["total"], 21.99)


if __name__ == "__main__":
	unittest.main()
