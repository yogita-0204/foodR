from datetime import datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from accounts.utils import get_or_create_wallet
from menu.models import Category, MenuItem
from payments.models import Payment
from shops.models import Shop

from .models import Order


User = get_user_model()


class OrderFlowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner@example.com",
            email="owner@example.com",
            password="password123",
            first_name="Owner",
        )
        Profile.objects.create(
            user=self.owner,
            role=Profile.ROLE_SHOP_OWNER,
            phone_number="9999999999",
        )
        self.shop = Shop.objects.create(
            name="Campus Cafe",
            description="Test shop",
            address="Main Block",
            phone_number="1111111111",
            email="cafe@example.com",
            owner=self.owner,
            opening_time=time(0, 0),
            closing_time=time(23, 59),
            max_orders_per_slot=5,
        )
        self.category = Category.objects.create(shop=self.shop, name="Snacks")
        self.menu_item = MenuItem.objects.create(
            shop=self.shop,
            category=self.category,
            name="Veg Sandwich",
            description="Fresh sandwich",
            price=Decimal("50.00"),
            is_available=True,
        )
        self.college_user = User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="password123",
            first_name="Student",
        )
        Profile.objects.create(
            user=self.college_user,
            role=Profile.ROLE_COLLEGE_USER,
            college_id="COL123",
            phone_number="8888888888",
        )

    def test_owner_dashboard_allows_shop_owner(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse("shops:owner_dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_owner_dashboard_blocks_college_user(self):
        self.client.force_login(self.college_user)

        response = self.client.get(reverse("shops:owner_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_checkout_creates_order_payment_and_clears_cart(self):
        wallet = get_or_create_wallet(self.college_user.profile)
        wallet.balance = Decimal("200.00")
        wallet.save(update_fields=["balance"])

        self.client.force_login(self.college_user)
        session = self.client.session
        session["cart_items"] = {str(self.menu_item.id): 2}
        session["cart_shop_id"] = self.shop.id
        session.save()

        pickup_date = timezone.localdate() + timedelta(days=1)
        pickup_time = timezone.make_aware(
            datetime.combine(pickup_date, time(12, 0))
        )

        response = self.client.post(
            reverse("orders:checkout"),
            {
                "pickup_time": pickup_time.strftime("%Y-%m-%dT%H:%M"),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("orders:list"))

        order = Order.objects.get(user=self.college_user, shop=self.shop)
        self.assertEqual(order.total_price, Decimal("100.00"))
        self.assertEqual(order.items.count(), 1)

        order_item = order.items.get()
        self.assertEqual(order_item.menu_item, self.menu_item)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, Decimal("50.00"))

        payment = Payment.objects.get(order=order)
        self.assertEqual(payment.payment_method, Payment.METHOD_WALLET)
        self.assertEqual(payment.payment_status, Payment.STATUS_PAID)

        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("100.00"))

        session = self.client.session
        self.assertNotIn("cart_items", session)
        self.assertNotIn("cart_shop_id", session)

    def test_wallet_checkout_rejects_insufficient_balance(self):
        wallet = get_or_create_wallet(self.college_user.profile)
        wallet.balance = Decimal("40.00")
        wallet.save(update_fields=["balance"])

        self.client.force_login(self.college_user)
        session = self.client.session
        session["cart_items"] = {str(self.menu_item.id): 1}
        session["cart_shop_id"] = self.shop.id
        session.save()

        pickup_date = timezone.localdate() + timedelta(days=1)
        pickup_time = timezone.make_aware(
            datetime.combine(pickup_date, time(12, 0))
        )

        response = self.client.post(
            reverse("orders:checkout"),
            {
                "pickup_time": pickup_time.strftime("%Y-%m-%dT%H:%M"),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Insufficient wallet balance.")
        self.assertFalse(Order.objects.filter(user=self.college_user, shop=self.shop).exists())

    def test_profile_top_up_adds_money_to_wallet(self):
        wallet = get_or_create_wallet(self.college_user.profile)
        self.client.force_login(self.college_user)

        response = self.client.post(
            reverse("accounts:profile"),
            {
                "amount": "150.00",
                "payment_source": "phonepe",
                "upi_id": "student@upi",
                "reference_id": "TXN12345",
            },
        )

        self.assertEqual(response.status_code, 302)
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("150.00"))