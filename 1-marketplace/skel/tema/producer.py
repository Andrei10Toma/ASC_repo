"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep
from typing import List, Tuple
from tema.product import Product
from tema.marketplace import Marketplace


class Producer(Thread):
    """
    Class that represents a producer.
    """

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        super().__init__(**kwargs)
        self.products: List[Tuple[Product, int, float]] = products
        self.marketplace: Marketplace = marketplace
        self.republish_wait_time: float = republish_wait_time
        self.id: int = self.marketplace.register_producer()

    def run(self):
        index_products_list: int = 0
        while True:
            if index_products_list == len(self.products):
                index_products_list = 0
            product: Product = self.products[index_products_list][0]
            quantity: int = self.products[index_products_list][1]
            wait_time: float = self.products[index_products_list][2]
            counter_quantity: int = 0
            while counter_quantity != quantity:
                product_published: bool = self.marketplace.publish(self.id, product)
                if product_published:
                    counter_quantity += 1
                    sleep(wait_time)
                else:
                    sleep(self.republish_wait_time)
            index_products_list += 1
