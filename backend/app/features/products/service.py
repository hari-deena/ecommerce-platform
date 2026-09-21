from app.common.service import BaseService
from app.features.products.models import Product
from app.features.products.repository import ProductRepository
from app.features.products.schemas import ProductCreate, ProductUpdate


class ProductService(BaseService[Product, ProductCreate, ProductUpdate]):
    not_found_message = "Product not found"

    def __init__(self, repository: ProductRepository) -> None:
        super().__init__(repository)
        self.repository: ProductRepository = repository
