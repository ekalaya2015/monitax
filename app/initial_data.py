"""
Put here any Python code that must be runned before application startup.
It is included in `init.sh` script.

By defualt `main` create a superuser if not exists
"""

import asyncio
from datetime import datetime
from decimal import Decimal
import random
import string
import uuid
import pendulum
from sqlalchemy import select
import app.utils.invnum_generator
from app.core import config, security
from app.core.utils import generate_random_password
# from app.core.session import async_session
from app.core.session import SessionLocal
from app.models.model import Role, User, Invoice


async def main() -> None:
    chars = string.digits
    print("Start initial data")
    async with SessionLocal() as session:
        result = await session.exec(
            select(User).where(User.username ==
                               config.settings.FIRST_SUPERUSER_EMAIL)
        )
        user = result.one_or_none()
        if user is None:
            new_superuser = User(
                username=config.settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=security.get_password_hash(
                    config.settings.FIRST_SUPERUSER_PASSWORD
                ),
                nik="".join(random.choice(chars) for i in range(16)),
                role=Role.admin,
                created_at=datetime.now(),
                modified_at=datetime.now(),
                first_name="Administrator",
                last_name="",
            )
            session.add(new_superuser)
            await session.commit()
            print("Superuser was created")
        else:
            print("Superuser already exists in database")
        devices = ['Raspigeek001', 'Raspigeek003']
        invdate = pendulum.now()
        for i in range(0, 3):
            randominvnum = generate_random_password()
            invnum = f'INV-{randominvnum}'
            random.shuffle(devices)
            total_value: float = random.randint(100, 999)*100.0
            tax_value: float = round(total_value*11.0/111.0, 2)
            invdate = invdate.add(minutes=10)
            inv = Invoice(id=str(uuid.uuid4()), invoice_num=invnum, invoice_date=invdate.to_iso8601_string(
            ), device_name=devices[0], username='ekalaya2015@gmail.com', total_value=total_value, tax_value=tax_value, created_at=pendulum.now().to_datetime_string(), modified_at=pendulum.now().to_datetime_string())
            session.add(inv)
            await session.commit()
        print("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
