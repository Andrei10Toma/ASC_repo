"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""


from typing import Dict, List, Tuple
from threading import RLock
import time
import logging
import unittest
from logging.handlers import RotatingFileHandler
from tema.product import Product, Tea, Coffee

MARKETPLACE_LOGGER = logging.getLogger('marketplace_logger')
MARKETPLACE_LOGGER.setLevel(logging.INFO)
HANDLER = RotatingFileHandler('marketplace.log', maxBytes=1048576, backupCount=10)
FORMATTER = logging.Formatter('%(asctime)s %(levelname)8s: %(message)s')
HANDLER.setFormatter(FORMATTER)
HANDLER.setLevel(logging.INFO)
logging.Formatter.converter = time.gmtime
MARKETPLACE_LOGGER.addHandler(HANDLER)

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer: int = queue_size_per_producer
        self.producer_counter: int = 0
        self.cart_counter: int = 0
        # dictionary from the id of the producer to a list that contains a list of products
        # and a flag that represents the cart where the product is found (-1 if the product
        # is not in a cart)
        self.producers_dict: Dict[int, List[List[Product, int]]] = {}
        # dictionary from the id of the cart to a list of tupples that contain a product and
        # an integer that represents the id of the producer where the product will be bought
        self.consumer_cart: Dict[int, List[Tuple[Product, int]]] = {}
        # dictionary from the cart id to the name of the consumer
        self.cart_consumer_name_dict: Dict[int, str] = {}
        self.lock = RLock()

    def register_producer(self):
        with self.lock:
            self.producer_counter += 1
            self.producers_dict[self.producer_counter - 1] = []
        MARKETPLACE_LOGGER.info('Producer registered with %d',
                                self.producer_counter - 1)
        return self.producer_counter - 1

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: int
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        MARKETPLACE_LOGGER.info('Adding %s from %d',
                                str(product), producer_id)
        if len(self.producers_dict[producer_id]) == self.queue_size_per_producer:
            MARKETPLACE_LOGGER.info('Queue full for %d', producer_id)
            return False
        self.producers_dict[producer_id].append([product, -1])
        MARKETPLACE_LOGGER.info('Added %s to %s', str(product),
                                str(self.producers_dict[producer_id]))
        return True

    def register_consumer_name_with_cart(self, name, cart_id):
        self.cart_consumer_name_dict[cart_id] = name
        MARKETPLACE_LOGGER.info('Client with %d has cart %s',
                                cart_id, name)

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        with self.lock:
            self.cart_counter += 1
            self.consumer_cart[self.cart_counter - 1] = []
        MARKETPLACE_LOGGER.info('Cart with %d added',
                                self.cart_counter - 1)
        return self.cart_counter - 1

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        MARKETPLACE_LOGGER.info('Adding %s in the cart %d', product, cart_id)
        for item in self.producers_dict.items():
            producer_products: List[List[Product, int]] = item[1]
            for producer_product in producer_products:
                # product found
                if producer_product[0] == product:
                    with self.lock:
                        # if it is not in someone's cart
                        if producer_product[1] == -1:
                            # add the product in the cart and the id of the producer
                            self.consumer_cart[cart_id].append((producer_product[0], item[0]))
                            # set the product as added in the cart
                            producer_product[1] = cart_id
                            MARKETPLACE_LOGGER.info('Added %s from %d to the cart %d',
                                                    str(product), item[0], cart_id)
                            return True
        MARKETPLACE_LOGGER.info('Product %s not found. Wait...', str(product))
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        MARKETPLACE_LOGGER.info('Removing %s from %d',
                                str(product), cart_id)
        cart: List[Tuple[Product, int]] = self.consumer_cart[cart_id]
        for cart_product in cart:
            if cart_product[0] == product:
                producer_products: List[List[Product, int]] = self.producers_dict[cart_product[1]]
                for producer_product in producer_products:
                    # product found
                    if producer_product[0] == product:
                        with self.lock:
                            # if the product is in someone's cart
                            if producer_product[1] == cart_id:
                                producer_product[1] = -1
                                cart.remove(cart_product)
                                MARKETPLACE_LOGGER.info('Product %s removed from cart %d\
                                                        and can be bought from producer %d',
                                                        str(product), cart_id, cart_product[1])
                                return

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        MARKETPLACE_LOGGER.info('Placing order from %d', cart_id)
        bought_products: List[Tuple[Product, int]] = self.consumer_cart[cart_id]
        for product in bought_products:
            producer_products: List[List[Product, int]] = self.producers_dict[product[1]]
            # remove the products from the producer's queue also
            for producer_product in producer_products:
                if producer_product[0] == product[0] and producer_product[1] == cart_id:
                    producer_products.remove(producer_product)
                    break
            print(f'{self.cart_consumer_name_dict[cart_id]} bought {product[0]}')
        # clear the cart
        self.consumer_cart[cart_id].clear()
        MARKETPLACE_LOGGER.info('Cart %d is now empty and products from cart removed \
            from producers queue', cart_id)

class TestMarketplace(unittest.TestCase):

    def setUp(self):
        self.marketplace = Marketplace(15)
        self.marketplace.register_producer()
        self.marketplace.register_producer()
        self.marketplace.publish(0, Tea("Ceai", 5, "London"))
        self.marketplace.publish(0, Coffee("Cafea", 10, "5.05", "MEDIUM"))
        self.marketplace.publish(1, Tea("Ceai", 5, "Turkish"))
        self.marketplace.new_cart()
        self.marketplace.new_cart()
        self.marketplace.register_consumer_name_with_cart('cons1', 0)
        self.marketplace.register_consumer_name_with_cart('cons2', 1)

    def test_register_producer(self):
        assert self.marketplace.producer_counter == 2
        assert len(self.marketplace.producers_dict) == 2

    def test_publish(self):
        assert self.marketplace.producers_dict[0] ==\
            [[Tea("Ceai", 5, "London"), -1], [Coffee("Cafea", 10, "5.05", "MEDIUM"), -1]]
        assert self.marketplace.producers_dict[1] == [[Tea("Ceai", 5, "Turkish"), -1]]

    def test_new_cart(self):
        assert self.marketplace.cart_counter == 2
        assert len(self.marketplace.consumer_cart) == 2

    def test_register_consumer_name_with_cart(self):
        assert self.marketplace.cart_consumer_name_dict[0] == 'cons1'
        assert self.marketplace.cart_consumer_name_dict[1] == 'cons2'

    def test_add_to_cart(self):
        self.marketplace.add_to_cart(0, Tea("Ceai", 5, "London"))
        self.marketplace.add_to_cart(1, Coffee("Cafea", 10, "5.05", "MEDIUM"))
        self.marketplace.add_to_cart(0, Tea("Ceai", 5, "Turkish"))
        assert self.marketplace.consumer_cart[0] == \
            [(Tea("Ceai", 5, "London"), 0), (Tea("Ceai", 5, "Turkish"), 1)]
        assert self.marketplace.consumer_cart[1] == [(Coffee("Cafea", 10, "5.05", "MEDIUM"), 0)]

    def test_remove_from_cart(self):
        self.marketplace.add_to_cart(0, Tea("Ceai", 5, "London"))
        self.marketplace.add_to_cart(1, Coffee("Cafea", 10, "5.05", "MEDIUM"))
        self.marketplace.add_to_cart(0, Tea("Ceai", 5, "Turkish"))
        self.marketplace.remove_from_cart(0, Tea("Ceai", 5, "Turkish"))
        assert self.marketplace.consumer_cart[0] == [(Tea("Ceai", 5, "London"), 0)]
        assert self.marketplace.consumer_cart[1] == [(Coffee("Cafea", 10, "5.05", "MEDIUM"), 0)]

    def test_place_order(self):
        self.marketplace.add_to_cart(0, Tea("Ceai", 5, "London"))
        self.marketplace.add_to_cart(1, Coffee("Cafea", 10, "5.05", "MEDIUM"))
        self.marketplace.add_to_cart(0, Tea("Ceai", 5, "Turkish"))
        self.marketplace.remove_from_cart(0, Tea("Ceai", 5, "Turkish"))
        self.marketplace.place_order(0)
        assert self.marketplace.consumer_cart[0] == []
        assert self.marketplace.producers_dict[0] == [[Coffee("Cafea", 10, "5.05", "MEDIUM"), 1]]
        self.marketplace.place_order(1)
        assert self.marketplace.consumer_cart[1] == []
        assert self.marketplace.producers_dict[0] == []
