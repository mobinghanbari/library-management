from sqlalchemy import Table, Column, Integer, String, DateTime, func, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# User section

class Ip(Base):
    __tablename__ = 'ips'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String(45), unique=True, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    user = relationship("User", back_populates="ips")


# Association table between roles and permissions
role_permission_association = Table('role_permission_association', Base.metadata,
                                    Column('role_id', Integer, ForeignKey('roles.id')),
                                    Column('permission_id', Integer, ForeignKey('permissions.id'))
                                    )


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    permissions = relationship("Permission", secondary=role_permission_association, back_populates="roles")


class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    roles = relationship("Role", secondary=role_permission_association, back_populates="permissions")


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(11), unique=True, nullable=False, index=True)
    is_activated = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey("roles.id"), default=3)
    password = Column(String(255), nullable=False)
    ip_check = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    role = relationship("Role")
    ips = relationship("Ip", back_populates="user")

    borrows = relationship("Borrow", back_populates="user", cascade="all, delete-orphan")


# Category
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(250), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Define relationships with cascade delete
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    books = relationship("Book", back_populates="category", cascade="all, delete-orphan")


# Author
class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(50), unique=True, nullable=False, index=True)
    nationality = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    books = relationship("Book", back_populates="author", cascade="all, delete-orphan")


# Book
class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), unique=True, nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("authors.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    stock = Column(Boolean, nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    published_at = Column(Date)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    category = relationship("Category", back_populates="books")
    author = relationship("Author", back_populates="books")

    images = relationship("BookImage", back_populates="book", cascade="all, delete-orphan")

    borrows = relationship("Borrow", back_populates="book", cascade="all, delete-orphan")


class BookImage(Base):
    __tablename__ = 'bookimages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"))
    image_url = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    book = relationship("Book", back_populates="images")


class Borrow(Base):
    __tablename__ = 'borrows'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    book_id = Column(Integer, ForeignKey("books.id"), index=True)
    borrow_date = Column(Date, default=func.current_date(), nullable=False)  # تغییر به Date و استفاده از func.current_date()
    return_date = Column(Date)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="borrows")
    book = relationship("Book", back_populates="borrows")