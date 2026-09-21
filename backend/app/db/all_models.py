"""Import every feature's models so `Base.metadata` is fully populated.

Used by Alembic (`alembic/env.py`) for autogenerate and by the test suite
(`tests/conftest.py`) for `Base.metadata.create_all`. Nothing in `app/` should
import this module for any other reason — routers/services import the
specific feature model they need directly.
"""

from app.features.audit_logs.models import AuditLog  # noqa: F401
from app.features.auth.models import PasswordResetToken, RefreshToken  # noqa: F401
from app.features.cart.models import Cart, CartItem  # noqa: F401
from app.features.categories.models import Category  # noqa: F401
from app.features.chatbot.models import ChatMessage, ChatSession, KnowledgeChunk  # noqa: F401
from app.features.contact.models import ContactEnquiry  # noqa: F401
from app.features.coupons.models import Coupon  # noqa: F401
from app.features.feedback.models import Feedback  # noqa: F401
from app.features.inventory.models import InventoryAdjustment  # noqa: F401
from app.features.news.models import NewsArticle  # noqa: F401
from app.features.orders.models import Order, OrderItem  # noqa: F401
from app.features.payments.models import Payment  # noqa: F401
from app.features.products.models import Product  # noqa: F401
from app.features.users.models import Address, User  # noqa: F401
from app.features.wishlist.models import WishlistItem  # noqa: F401
