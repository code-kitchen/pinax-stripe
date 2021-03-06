import stripe
from django.utils.encoding import smart_str

from .. import utils
from .. import models
from .. actions import skus

def sync_products():
    """
    Synchronizes all the products from the Stripe API
    """
    try:
        products = stripe.Product.auto_paging_iter()
    except AttributeError:
        products = iter(stripe.Product.list().data)

    for product in products:
        sync_product_from_stripe_data(product)

def sync_product_from_stripe_data(stripe_product):
    """
    Create or update the product represented by the data from a Stripe API query.

    Args:
        stripe_product: the data representing a sku object in the Stripe API

    Returns:
        a pinax.stripe.models.Product object
    """

    stripe_product_id = stripe_product["id"]

    defaults = {
        'active': stripe_product.get("active"),
        'attributes': stripe_product.get("attributes"),
        'caption': stripe_product.get("caption"),
        'description': stripe_product.get("description"),
        'images': stripe_product.get("images"),
        'livemode': stripe_product.get("livemode"),
        'metadata': stripe_product.get("metadata"),
        'name': stripe_product.get("name"),
        'package_dimensions': stripe_product.get("package_dimensions"),
        'shippable': stripe_product.get("shippable")
    }

    obj, created = models.Product.objects.get_or_create(stripe_id=stripe_product_id)
    obj = utils.update_with_defaults(obj, defaults, created)
    skus.sync_skus_from_product(obj)
    return obj

def create(name, p_id="", caption="", description="", active=True, shippable=False, attributes=None, images=None, metadata=None, package_dimensions=None):
    """
    Creates a product

    Args:
        name: The product’s name, meant to be displayable to the customer.
        p_id: optionally, Unique identifier for the object, If an ID isn't provided, we'll generate one for you.
        caption: optionally,  A short one-line description of the product, meant to be displayable to the customer.
        description: optionally,  The product’s description, meant to be displayable to the customer.
        active: optionally,  Whether or not the product is currently available for purchase. Defaults to True
        shippable: optionally,  Whether this product is shipped (i.e. physical goods). Defaults to False.
        attributes: optionally,  A list of up to 5 alphanumeric attributes that each SKU can provide values for (e.g. ["color", "size"]).
        images: optionally,  A list of up to 8 URLs of images for this product, meant to be displayable to the customer.
        metadata: optionally,  A set of key/value pairs that you can attach to a product object. It can be useful for storing additional information about the product in a structured format.
        package_dimensions: optionally,  The dimensions of this product for shipping purposes, all values are required. e.g
        {
            "height": 20
            "length": 21
            "weight": 22
            "width": 23
        }

    Returns:
        the data representing the product object that was created
    """

    product_params = {
        "name": name,
        "active": active,
        "shippable": shippable
    }

    if p_id:
        product_params.update({"id": p_id})

    if caption:
        product_params.update({"caption": caption})

    if description:
        product_params.update({"description": description})

    if attributes:
        product_params.update({"attributes": attributes})

    if images:
        product_params.update({"images": images})

    if metadata:
        product_params.update({"images": metadata})

    if package_dimensions:
        product_params.update({"package_dimensions": package_dimensions})

    stripe_product = stripe.Product.create(**product_params)
    return sync_product_from_stripe_data(stripe_product)

def update(product, name="", caption="", description="", active=None, shippable=False, attributes=None, images=None, metadata=None, package_dimensions=None):
    """
    Updates a product

    Args:
        product: the product to update
        name: optionally, whether or not to charge immediately
        caption: optionally, whether or not to charge immediately
        description: optionally, whether or not to charge immediately
        active: optionally, whether or not to charge immediately
        shippable: optionally, whether or not to charge immediately
        attributes: optionally, whether or not to charge immediately
        images: optionally, whether or not to charge immediately
        metadata: optionally, whether or not to charge immediately
        package_dimensions: optionally, whether or not to charge immediately
    """

    stripe_product = product.stripe_product

    if name:
        stripe_product.name = name
    if caption:
        stripe_product.caption = caption
    if description:
        stripe_product.description = description
    if active is not None:
        stripe_product.active = active
    if shippable:
        stripe_product.shippable = shippable
    if attributes:
        stripe_product.attributes = attributes
    if images:
        stripe_product.images = images
    if metadata:
        stripe_product.metadata = metadata
    if package_dimensions:
        stripe_product.images = package_dimensions

    stripe_product.save()
    sync_product_from_stripe_data(stripe_product)

def retrieve(product_id):
    """
    Retrieve a sku object from Stripe's API

    Stripe throws an exception if the product has been deleted that we are
    attempting to sync. In this case we want to just silently ignore that
    exception but pass on any other.

    Args:
        product_id: the Stripe ID of the product you are fetching

    Returns:
        the data for a order object from the Stripe API
    """
    if not product_id:
        return

    try:
        return stripe.Product.retrieve(product_id)
    except stripe.InvalidRequestError as e:
        if smart_str(e).find("No such product") == -1:
            raise
        else:
            # Not Found
            return None

def delete(product):
    """
    delete a product

    Args:
        product: the product to delete
    """
    stripe_product = stripe.Product.retrieve(product.stripe_id)
    stripe_product.delete()
    product.delete()