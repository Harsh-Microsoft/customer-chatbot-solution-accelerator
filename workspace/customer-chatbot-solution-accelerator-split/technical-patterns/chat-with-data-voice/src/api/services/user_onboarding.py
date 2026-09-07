import logging
import random
from datetime import datetime, timedelta
from typing import List

from cosmos_service import get_cosmos_service
from models import OrderStatus, Transaction, TransactionItem

# Ported from chat-app/backend/app/services/user_onboarding.py (plan row 13).
# `create_fallback_demo_orders` no longer branches on a hardcoded scenario
# enum with Contoso Paints/Health/Banking product names: it seeds the demo
# order from whatever catalog items the active scenario's manifest has
# loaded, via `cosmos_service.get_featured_catalog_items`, matching the
# manifest-driven de-domaining used elsewhere in this pattern. Not currently
# invoked from `routers/auth.py` -- see that module's comment on why user
# persistence is out of scope for this pattern's `DatabaseService`.

logger = logging.getLogger(__name__)

SAMPLE_USER_IDS = ["sample-user-1", "sample-user-2", "sample-user-3"]


async def create_demo_order_history(user_id: str) -> List[Transaction]:
    cosmos_service = get_cosmos_service()

    existing_orders = await cosmos_service.get_orders_by_customer(user_id, limit=1)
    if existing_orders:
        logger.info(f"User {user_id} already has order history, skipping demo creation")
        return []

    logger.info(
        f"Creating demo order history for new user: {user_id} by replicating sample user orders"
    )

    demo_orders = []

    # Get all orders from sample users
    all_sample_orders = []
    for sample_user_id in SAMPLE_USER_IDS:
        try:
            sample_orders = await cosmos_service.get_orders_by_customer(
                sample_user_id, limit=50
            )
            all_sample_orders.extend(sample_orders)
            logger.info(
                f"Found {len(sample_orders)} orders for sample user {sample_user_id}"
            )
        except Exception as e:
            logger.error(f"Failed to get orders for sample user {sample_user_id}: {e}")

    if not all_sample_orders:
        logger.warning("No sample orders found, falling back to catalog-derived demo orders")
        return await create_fallback_demo_orders(user_id)

    # Randomly select orders to replicate (between 3-8 orders)
    num_orders_to_replicate = min(random.randint(3, 8), len(all_sample_orders))
    selected_orders = random.sample(all_sample_orders, num_orders_to_replicate)

    logger.info(f"Replicating {len(selected_orders)} orders from sample users")

    for idx, sample_order in enumerate(selected_orders, start=1):
        try:
            # Create new order based on sample order
            new_order_number = f"ORD-{user_id[:8].upper()}-{idx:04d}"

            # Create transaction items
            items = []
            for item_data in sample_order.get("items", []):
                items.append(
                    TransactionItem(
                        product_id=item_data.get("product_id", ""),
                        product_title=item_data.get("product_title", ""),
                        quantity=item_data.get("quantity", 1),
                        unit_price=item_data.get("unit_price", 0.0),
                        total_price=item_data.get("total_price", 0.0),
                    )
                )

            # Create new transaction
            transaction = Transaction(
                id=f"order-{user_id}-{idx}",
                user_id=user_id,
                order_number=new_order_number,
                status=OrderStatus.DELIVERED,  # Set all replicated orders as delivered
                items=items,
                subtotal=sample_order.get("subtotal", 0.0),
                tax=sample_order.get("tax", 0.0),
                shipping=sample_order.get("shipping", 0.0),
                total=sample_order.get("total", 0.0),
                shipping_address=sample_order.get(
                    "shipping_address",
                    {
                        "street": "123 Demo Street",
                        "city": "Seattle",
                        "state": "WA",
                        "zip": "98101",
                        "country": "USA",
                    },
                ),
                payment_method=sample_order.get("payment_method", "Credit Card"),
                payment_reference=f"PAY-{random.randint(100000, 999999)}",
                created_at=datetime.utcnow()
                - timedelta(
                    days=random.randint(1, 180)
                ),  # Random date within last 6 months
                updated_at=datetime.utcnow(),
            )

            # Save to database
            transaction_dict = transaction.model_dump()
            transaction_dict["created_at"] = transaction.created_at.isoformat()
            transaction_dict["updated_at"] = transaction.updated_at.isoformat()

            cosmos_service.transactions_container.create_item(transaction_dict)  # type: ignore
            demo_orders.append(transaction)
            logger.info(
                f"Created replicated order {new_order_number} for user {user_id}"
            )

        except Exception as e:
            logger.error(f"Failed to replicate order: {e}")

    logger.info(
        f"Successfully created {len(demo_orders)} replicated orders for user {user_id}"
    )
    return demo_orders


async def create_fallback_demo_orders(user_id: str) -> List[Transaction]:
    """Seed one demo order from the active scenario's catalog when no sample-user history exists."""
    logger.info("Creating fallback demo order from the active catalog")
    cosmos_service = get_cosmos_service()

    try:
        catalog_items = await cosmos_service.get_featured_catalog_items(limit=3)
    except Exception as e:
        logger.error(f"Failed to load catalog items for fallback demo order: {e}")
        catalog_items = []

    if not catalog_items:
        logger.warning("No catalog items available; skipping fallback demo order creation")
        return []

    now = datetime.utcnow()
    order_date = now - timedelta(days=15)

    items = []
    subtotal = 0.0
    for catalog_item in catalog_items:
        unit_price = catalog_item.price or 0.0
        items.append(
            TransactionItem(
                product_id=catalog_item.id,
                product_title=catalog_item.title,
                quantity=1,
                unit_price=unit_price,
                total_price=unit_price,
            )
        )
        subtotal += unit_price

    tax = round(subtotal * 0.08, 2)
    shipping = 5.99 if subtotal > 0 else 0.0
    total = round(subtotal + tax + shipping, 2)

    transaction = Transaction(
        id=f"order-{user_id}-1",
        user_id=user_id,
        order_number=f"ORD-{user_id[:8].upper()}-0001",
        status=OrderStatus.DELIVERED,
        items=items,
        subtotal=subtotal,
        tax=tax,
        shipping=shipping,
        total=total,
        shipping_address={
            "street": "123 Demo Street",
            "city": "Seattle",
            "state": "WA",
            "zip": "98101",
            "country": "USA",
        },
        payment_method="Credit Card",
        payment_reference=f"PAY-{random.randint(100000, 999999)}",
        created_at=order_date,
        updated_at=now,
    )

    transaction_dict = transaction.model_dump()
    transaction_dict["created_at"] = transaction.created_at.isoformat()
    transaction_dict["updated_at"] = transaction.updated_at.isoformat()

    cosmos_service.transactions_container.create_item(transaction_dict)  # type: ignore
    logger.info(f"Created fallback demo order for user {user_id}")
    return [transaction]
