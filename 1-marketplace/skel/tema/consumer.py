"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread, RLock
from time import sleep
from typing import Dict, List
from tema.product import Product
from tema.marketplace import Marketplace


class Consumer(Thread):
    """
    Class that represents a consumer.
    """
    ADD = 'add'
    REMOVE = 'remove'
    TYPE = 'type'
    PRODUCT = 'product'
    QUANTITY = 'quantity'

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        super().__init__(**kwargs)
        self.carts: List[List[Dict[str, object]]] = carts
        self.marketplace: Marketplace = marketplace
        self.retry_wait_time: float = retry_wait_time
        self.name = kwargs['name']
        self.cart_id = self.marketplace.new_cart()

    def run(self):
        self.marketplace.register_consumer_name_with_cart(self.name, self.cart_id)
        for cart in self.carts:
            for operation in cart:
                op_type: str = operation[self.TYPE]
                op_product: Product = operation[self.PRODUCT]
                op_quantity: int = operation[self.QUANTITY]
                if op_type == self.ADD:
                    while op_quantity != 0:
                        added_to_cart = self.marketplace.add_to_cart(self.cart_id, op_product)
                        if added_to_cart:
                            op_quantity -= 1
                        else:
                            sleep(self.retry_wait_time)
                elif op_type == self.REMOVE:
                    while op_quantity != 0:
                        self.marketplace.remove_from_cart(self.cart_id, op_product)
                        op_quantity -= 1
            self.marketplace.place_order(self.cart_id)
