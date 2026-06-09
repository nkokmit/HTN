from unittest.mock import Mock, patch

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from .models import Cart
from .views import AddCartItem


class AddCartItemTests(TestCase):
	def setUp(self):
		self.factory = APIRequestFactory()
		self.cart = Cart.objects.create(customer_id=101)

	@patch("app.views.requests.get")
	def test_add_book_item_uses_product_service(self, mock_get):
		mock_response = Mock()
		mock_response.status_code = 200
		mock_response.json.return_value = {
			"id": 11,
			"name": "Clean Code",
			"price": "25.50",
			"stock": 7,
			"product_type": "BOOK",
		}
		mock_get.return_value = mock_response

		request = self.factory.post(
			"/cart-items/",
			{
				"cart": self.cart.id,
				"product_id": 11,
				"quantity": 2,
			},
			format="json",
		)

		response = AddCartItem.as_view()(request)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["product_id"], 11)
		self.assertEqual(response.data["quantity"], 2)

