import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import tempfile
import os

# Тесты для CRUD операций
@pytest.mark.asyncio
async def test_create_item():
    # Создаем тестовую сессию
    fd, path = tempfile.mkstemp(prefix="tmp_test_item_", suffix=".sqlite")
    os.close(fd)
    
    try:
        db_url = f"sqlite+aiosqlite:///{path}"
        engine = create_async_engine(db_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        session_local = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with session_local() as session:
            # Создаем тестовый item
            item_data = schemas.ItemCreate(name="Тестовый предмет", description="Описание тестового предмета")
            created_item = await crud.create_item(db=session, item=item_data)
            
            assert created_item.name == item_data.name
            assert created_item.description == item_data.description
            assert created_item.id is not None
    
    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


@pytest.mark.asyncio
async def test_get_item():
    fd, path = tempfile.mkstemp(prefix="tmp_test_item_", suffix=".sqlite")
    os.close(fd)
    
    try:
        db_url = f"sqlite+aiosqlite:///{path}"
        engine = create_async_engine(db_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        session_local = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with session_local() as session:
            # Создаем тестовый item
            item_data = schemas.ItemCreate(name="Тестовый предмет", description="Описание тестового предмета")
            created_item = await crud.create_item(db=session, item=item_data)
            
            # Получаем item по ID
            retrieved_item = await crud.get_item(db=session, item_id=created_item.id)
            
            assert retrieved_item is not None
            assert retrieved_item.id == created_item.id
            assert retrieved_item.name == created_item.name
            assert retrieved_item.description == created_item.description
    
    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


@pytest.mark.asyncio
async def test_get_items():
    fd, path = tempfile.mkstemp(prefix="tmp_test_items_", suffix=".sqlite")
    os.close(fd)
    
    try:
        db_url = f"sqlite+aiosqlite:///{path}"
        engine = create_async_engine(db_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        session_local = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with session_local() as session:
            # Создаем несколько тестовых items
            item_data1 = schemas.ItemCreate(name="Тестовый предмет 1", description="Описание 1")
            item_data2 = schemas.ItemCreate(name="Тестовый предмет 2", description="Описание 2")
            await crud.create_item(db=session, item=item_data1)
            await crud.create_item(db=session, item=item_data2)
            
            # Получаем список items
            items = await crud.get_items(db=session, skip=0, limit=10)
            
            assert len(items) >= 2
    
    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


@pytest.mark.asyncio
async def test_create_user():
    fd, path = tempfile.mkstemp(prefix="tmp_test_user_", suffix=".sqlite")
    os.close(fd)
    
    try:
        db_url = f"sqlite+aiosqlite:///{path}"
        engine = create_async_engine(db_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        session_local = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with session_local() as session:
            # Создаем тестового пользователя
            user_data = schemas.UserCreate(username="testuser", email="test@example.com", full_name="Тестовый Пользователь")
            created_user = await crud.create_user(db=session, user=user_data)
            
            assert created_user.username == user_data.username
            assert created_user.email == user_data.email
            assert created_user.full_name == user_data.full_name
            assert created_user.id is not None
    
    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


@pytest.mark.asyncio
async def test_get_user():
    fd, path = tempfile.mkstemp(prefix="tmp_test_user_", suffix=".sqlite")
    os.close(fd)
    
    try:
        db_url = f"sqlite+aiosqlite:///{path}"
        engine = create_async_engine(db_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        session_local = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with session_local() as session:
            # Создаем тестового пользователя
            user_data = schemas.UserCreate(username="testuser", email="test@example.com", full_name="Тестовый Пользователь")
            created_user = await crud.create_user(db=session, user=user_data)
            
            # Получаем пользователя по ID
            retrieved_user = await crud.get_user(db=session, user_id=created_user.id)
            
            assert retrieved_user is not None
            assert retrieved_user.id == created_user.id
            assert retrieved_user.username == created_user.username
            assert retrieved_user.email == created_user.email
            assert retrieved_user.full_name == created_user.full_name
    
    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass


@pytest.mark.asyncio
async def test_get_users():
    fd, path = tempfile.mkstemp(prefix="tmp_test_users_", suffix=".sqlite")
    os.close(fd)
    
    try:
        db_url = f"sqlite+aiosqlite:///{path}"
        engine = create_async_engine(db_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        session_local = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with session_local() as session:
            # Создаем несколько тестовых пользователей
            user_data1 = schemas.UserCreate(username="testuser1", email="test1@example.com", full_name="Пользователь 1")
            user_data2 = schemas.UserCreate(username="testuser2", email="test2@example.com", full_name="Пользователь 2")
            await crud.create_user(db=session, user=user_data1)
            await crud.create_user(db=session, user=user_data2)
            
            # Получаем список пользователей
            users = await crud.get_users(db=session, skip=0, limit=10)
            
            assert len(users) >= 2
    
    finally:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass