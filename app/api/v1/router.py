from fastapi import APIRouter

from app.features.audit_logs.router import router as audit_logs_router
from app.features.auth.router import router as auth_router
from app.features.cart.router import router as cart_router
from app.features.categories.router import router as categories_router
from app.features.chatbot.router import router as chatbot_router
from app.features.contact.router import admin_router as contact_admin_router
from app.features.contact.router import router as contact_router
from app.features.coupons.router import router as coupons_router
from app.features.dashboard.router import router as dashboard_router
from app.features.feedback.router import admin_router as feedback_admin_router
from app.features.feedback.router import router as feedback_router
from app.features.inventory.router import router as inventory_router
from app.features.news.router import admin_router as news_admin_router
from app.features.news.router import router as news_router
from app.features.orders.router import admin_router as orders_admin_router
from app.features.orders.router import router as orders_router
from app.features.payments.router import admin_router as payments_admin_router
from app.features.payments.router import router as payments_router
from app.features.products.router import router as products_router
from app.features.users.router import admin_router as users_admin_router
from app.features.users.router import router as users_router
from app.features.wishlist.router import router as wishlist_router

api_router = APIRouter()

# Public / customer-facing
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(products_router)
api_router.include_router(categories_router)
api_router.include_router(news_router)
api_router.include_router(contact_router)
api_router.include_router(feedback_router)
api_router.include_router(cart_router)
api_router.include_router(wishlist_router)
api_router.include_router(orders_router)
api_router.include_router(payments_router)
api_router.include_router(chatbot_router)

# Admin-only surfaces. Each is mounted directly on `api_router` — not nested
# inside its feature's public router — so an admin_router already carrying its
# own `/admin/...` prefix doesn't get double-prefixed (e.g. `/admin/users`, not
# `/users/admin/users`). Every route below is additionally guarded by
# `require_admin` inside the router itself.
api_router.include_router(users_admin_router)
api_router.include_router(news_admin_router)
api_router.include_router(feedback_admin_router)
api_router.include_router(contact_admin_router)
api_router.include_router(orders_admin_router)
api_router.include_router(payments_admin_router)
api_router.include_router(inventory_router)
api_router.include_router(coupons_router)
api_router.include_router(audit_logs_router)
api_router.include_router(dashboard_router)
