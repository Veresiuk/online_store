import pytest
from online_store.models import Product
from online_store.repositories import CategoryRepository, ProductRepository
from online_store.services import StoreService


def test_create_and_read_product(session):
    cat_repo = CategoryRepository(session)
    prod_repo = ProductRepository(session)

    category = cat_repo.add("Смартфони")
    product = prod_repo.add(
        Product(
            name="iPhone 15",
            price=38000.0,
            quantity=10,
            category_id=category.id,
            description="Флагман",
        )
    )

    assert product.id is not None
    loaded = prod_repo.get_by_id(product.id)
    assert loaded is not None
    assert loaded.name == "iPhone 15"
    assert loaded.category.name == "Смартфони"


def test_update_product(session):
    cat_repo = CategoryRepository(session)
    prod_repo = ProductRepository(session)

    category = cat_repo.add("Планшети")
    product = prod_repo.add(
        Product(name="iPad", price=25000.0, quantity=5, category_id=category.id)
    )

    updated = prod_repo.update_price_and_quantity(product.id, price=23000.0, quantity=4)
    assert updated.price == 23000.0
    assert updated.quantity == 4


def test_delete_product(session):
    cat_repo = CategoryRepository(session)
    prod_repo = ProductRepository(session)

    category = cat_repo.add("Чохли")
    product = prod_repo.add(
        Product(name="Силіконовий чохол", price=400.0, quantity=50, category_id=category.id)
    )

    result = prod_repo.delete(product.id)
    assert result is True
    assert prod_repo.get_by_id(product.id) is None


def test_filter_by_category(session):
    cat_repo = CategoryRepository(session)
    prod_repo = ProductRepository(session)

    cat1 = cat_repo.add("Монітори")
    cat2 = cat_repo.add("Клавіатури")

    prod_repo.add(Product(name="Dell 27", price=9000.0, quantity=2, category_id=cat1.id))
    prod_repo.add(Product(name="LG 24", price=6000.0, quantity=3, category_id=cat1.id))
    prod_repo.add(Product(name="Keychron K2", price=4000.0, quantity=5, category_id=cat2.id))

    monitors = prod_repo.find_by_category(cat1.id)
    assert len(monitors) == 2


def test_stock_value_and_most_expensive(session):
    cat_repo = CategoryRepository(session)
    prod_repo = ProductRepository(session)
    service = StoreService(session)

    cat = cat_repo.add("Аудіо")
    prod_repo.add(Product(name="Колонки", price=2000.0, quantity=3, category_id=cat.id))
    prod_repo.add(Product(name="Навушники", price=5000.0, quantity=2, category_id=cat.id))

    assert service.get_total_stock_value() == 16000.0
    most_expensive = service.get_most_expensive_product()
    assert most_expensive.name == "Навушники"


def test_purchase_product_success(session):
    cat_repo = CategoryRepository(session)
    prod_repo = ProductRepository(session)
    service = StoreService(session)

    cat = cat_repo.add("Носії")
    product = prod_repo.add(
        Product(name="SSD 1TB", price=3200.0, quantity=10, category_id=cat.id)
    )

    updated_product = service.purchase_product(product.id, 4)
    assert updated_product.quantity == 6


def test_purchase_product_insufficient_stock_rollback(session):
    cat_repo = CategoryRepository(session)
    prod_repo = ProductRepository(session)
    service = StoreService(session)

    cat = cat_repo.add("Носії")
    product = prod_repo.add(
        Product(name="Флешка 64GB", price=350.0, quantity=3, category_id=cat.id)
    )

    # При спробі купити більше залишку викликається помилка
    with pytest.raises(ValueError, match="Недостатньо товару на складі"):
        service.purchase_product(product.id, 10)

    session.refresh(product)
    # Перевірка відкату (rollback): залишок не змінився
    assert product.quantity == 3