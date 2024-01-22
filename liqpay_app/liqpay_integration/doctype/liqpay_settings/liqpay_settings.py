# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

from tkinter import N, NO
from uuid import uuid4
import frappe
from http.client import HTTPException
from frappe.model.document import Document
from liqpay import LiqPay
import requests
import json



class LiqPaySettings(Document):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.liqpay = LiqPay(self.public_key, self.get_password(fieldname="private_key", raise_exception=False))
        self.data_storage: dict = {
            "version": "3",
            "public_key": self.public_key
        }
        self.logger = frappe.logger()
        
    def validate_transaction_currency(self, currency):
        if currency not in ["UAH", "USD", "EUR"]:
            raise ValueError
    
    def validate_minimum_transaction_amount(self, currency, amount):
        if amount <= 1:
            raise ValueError(f"Invalid Transaction Amount. Minimum is 1, current: {amount}")

    def get_payment_url(
            self,
            order_id: str,
            amount,
            title: str = "Default Title",
            description: str = "",
            currency: str = "UAH",
            product_name: str = None,
            product_url: str = None,
            **kwargs
        ) -> str:
        """
        Creates payments url with liqpay api call
        :param order_id: unique id for specific payment
        :param amount: price for checkout
        :param text: comment for customer
        :return: url of checkout
        """
        data = {key: value for key, value in self.data_storage.items()}
        if isinstance(description, bytes):
            description = description.decode('utf-8')
        data["action"] = "pay"
        data["amount"] = str(amount)
        data["currency"] = currency
        data["language"] = "uk"
        data["description"] = description
        data["order_id"] = order_id
        
        payment_request = frappe.get_doc("Payment Request", {'name': order_id})
        sales_order_name = payment_request.reference_name
        
        data["result_url"] = f"{frappe.utils.get_url('orders')}/{sales_order_name}"
        
        callback_url = f"{frappe.utils.get_url()}/api/method/liqpay_app.liqpay_integration.doctype.liqpay_settings.liqpay_settings.callback_handler"
        data["server_url"] = callback_url
        if product_name:
            data["product_name"] = product_name
        if product_url:
            data["product_url"] = product_url
        data_to_sign = self.liqpay.data_to_sign(data)
        params = {
            "data": data_to_sign,
            "signature": self.liqpay.cnb_signature(data)
        }
        
        response = None
        try:
            response = requests.post("https://www.liqpay.ua/api/3/checkout", data=params)
            if response.status_code == 200:
                return response.url
            else:
                self.logger.error(f"[$] Incorrect status code of payment. data={data}, params={params}")
                raise HTTPException(401, "fIncorrect status code of payment. data={data}, params={params}")

        except Exception as error:
            self.logger.error(f"[$] Error from liqpay: {str(error)}")
            raise error
        
    def get_order_status_from_liqpay(self, order_id):
        data = {key: value for key, value in self.data_storage.items()}
        data["action"] = "status"
        data["order_id"] = order_id
        response = self.liqpay.api("request", data)
        if response.get("status") == "error":
            return (f"Error with payment check. Code: {response.get('err_code')}. Description: {response.get('err_description')}")
        if response.get("action") == "pay":
            if response.get("public_key") == self.public_key:
                return response
        return "Get order status: action != pay or public_key invalid"
    
    
@frappe.whitelist(allow_guest=True, methods=["POST"])
def callback_handler(data: str):
    liqpay = frappe.get_single("LiqPay Settings")
    decoded_data = liqpay.liqpay.decode_data_from_str(data)
        
    status = decoded_data.get('status')
    order_id = decoded_data.get('order_id')
    
    if status == "success":
    
        payment_request = frappe.get_doc("Payment Request", order_id)
        payment_request.set_as_paid()
        print(f"Payment of order {order_id} succeed")
        
        
        
    
    


    