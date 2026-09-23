from app.common.service import BaseService
from app.features.categories.models import Category
from app.features.categories.repository import CategoryRepository
from app.features.categories.schemas import CategoryCreate, CategoryUpdate

# TODO: enforce unique slug at the service layer (raise AlreadyExistsError) once
# the final category taxonomy is confirmed with the client (PRD §15).


class CategoryService(BaseService[Category, CategoryCreate, CategoryUpdate]):
    not_found_message = "Category not found"

    def __init__(self, repository: CategoryRepository) -> None:
        super().__init__(repository)
        self.repository: CategoryRepository = repository
