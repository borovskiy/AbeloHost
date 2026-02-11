import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List
import random

from fastapi import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_connector import get_db
from app.models import TransactionModel
from app.models.user_models import UserModel
from app.enums.enum_status import TypeStatusEnum
from app.enums.enum_type_pay import TypePayEnum


async def initialize_sample_data():
    """
    Инициализирует тестовые данные при запуске приложения.
    Если в БД уже есть пользователи, ничего не делает.
    Иначе создаёт 100 пользователей с 100 транзакциями у каждого (всего 10 000 транзакций).
    """
    # Получаем сессию
    session_gen = get_db()
    session: AsyncSession = await session_gen.__anext__()

    try:
        # Проверяем, есть ли пользователи в БД
        count_stmt = select(func.count(UserModel.id))
        user_count = await session.scalar(count_stmt)

        if user_count > 0:
            # Пропускаем инициализацию т.к. данные уже есть
            logging.info("Тестовые данные уже существуют в базе данных")
            return

        logging.info("Начинаем создание тестовых данных...")

        # Создаем 100 пользователей
        sample_users = []
        for i in range(1, 101):
            user = UserModel(
                email=f"user{i}@example.com",
                name=f"User {i}",
                hashed_password=f"hashed_password_{i}"  # В реальном приложении используйте хеширование
            )
            sample_users.append(user)
        session.add_all(sample_users)
        await session.flush()  # Получаем ID пользователей
        logging.info(f"Создано {len(sample_users)} пользователей")
        # Создаем транзакции
        sample_transactions = []
        # Определяем диапазон дат: последние 2 года
        now = datetime.now()
        two_years_ago = now - timedelta(days=730)  # 2 года = 730 дней

        # Статусы и типы для сбалансированного распределения
        statuses = [TypeStatusEnum.SUCCESSFUL, TypeStatusEnum.FAILED]
        types = [TypePayEnum.PAYMENT, TypePayEnum.INVOICE]

        total_transactions = 0

        for i, user in enumerate(sample_users, 1):
            # Создаем 100 транзакций для каждого пользователя
            for j in range(100):
                # Случайная дата в пределах последних 2 лет
                random_seconds = random.randint(0, int((now - two_years_ago).total_seconds()))
                transaction_date = two_years_ago + timedelta(seconds=random_seconds)

                # Случайная сумма от 1 до 1000
                amount = Decimal(f"{round(random.uniform(1, 1000), 2)}")

                # Сбалансированное распределение статусов (50/50)
                status = statuses[j % 2]

                # Сбалансированное распределение типов (50/50)
                trans_type = types[j % 2]

                transaction = TransactionModel(
                    date_pay=transaction_date,
                    sum_pay=amount,
                    status=status,
                    type=trans_type,
                    user_id=user.id
                )
                sample_transactions.append(transaction)

            total_transactions += 100

            # Периодически сохраняем для избежания переполнения памяти
            if i % 10 == 0:
                session.add_all(sample_transactions)
                await session.flush()
                sample_transactions = []
                logging.info(f"Обработано {i} пользователей, создано {total_transactions} транзакций")

        # Добавляем оставшиеся транзакции
        if sample_transactions:
            session.add_all(sample_transactions)

        await session.commit()
        logging.info(f"✅ Успешно создано: 100 пользователей и {total_transactions} транзакций")

    except Exception as e:
        await session.rollback()
        logging.error(f"❌ Ошибка при создании тестовых данных: {e}")
        raise
    finally:
        await session.close()