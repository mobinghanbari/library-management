import random
from faker import Faker
from sqlalchemy.orm import Session
from database.models import Base, Author, Book, Role, Permission, Category
from database.connection import engine, get_db

fake = Faker()

def seed_database():
    # create new session for db
    db = next(get_db())

    # delete exist tables and create them again
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Add permissions
    permissions = []
    for slug in ['READ', 'CREATE', 'UPDATE', 'DELETE']:
        permission = Permission(slug=slug)
        permissions.append(permission)
        db.add(permission)

    db.commit()

    # Add roles
    admin_role = Role(slug='admin', permissions=permissions)
    manager_role = Role(slug='manager', permissions=[p for p in permissions if p.slug != 'DELETE'])
    user_role = Role(slug='user', permissions=[p for p in permissions if p.slug == 'READ'])

    roles = [admin_role, manager_role, user_role]
    for role in roles:
        db.add(role)

    db.commit()

    # Add authors
    authors = []
    for _ in range(10):
        author = Author(
            full_name=fake.name(),
            nationality=fake.country(),
        )
        authors.append(author)
        db.add(author)

    db.commit()

    # Add categories
    parent_categories = []
    category_names = set()
    for _ in range(5):
        name = fake.word()
        while name in category_names:
            name = fake.word()
        category_names.add(name)

        category = Category(
            name=name,
            description=fake.sentence(),
            parent_id=None
        )
        parent_categories.append(category)
        db.add(category)

    db.commit()

    # Add child categories
    for parent_category in parent_categories:
        for _ in range(2):  # هر دسته‌بندی والد 2 دسته‌بندی فرزند داشته باشد
            name = fake.word()
            while name in category_names:
                name = fake.word()
            category_names.add(name)

            category = Category(
                name=name,
                description=fake.sentence(),
                parent_id=parent_category.id
            )
            db.add(category)

    db.commit()

    # Add books
    titles = set()
    for _ in range(100):
        title = fake.sentence(nb_words=3)
        while title in titles:
            title = fake.sentence(nb_words=3)
        titles.add(title)

        book = Book(
            title=title,
            author_id=random.choice(authors).id,
            category_id=random.choice(parent_categories).id, 
            stock=fake.boolean(),
            quantity=fake.random_int(min=1, max=10),
            published_at=fake.date_this_century()
        )
        db.add(book)

    db.commit()

    db.close()

    print("Database seeded successfully!")

seed_database()
