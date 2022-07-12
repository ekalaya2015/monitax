"""
Put here any Python code that must be runned before application startup.
It is included in `init.sh` script.

By defualt `main` create a superuser if not exists
"""

import asyncio
from datetime import datetime
import random
import string
from sqlalchemy import select

from app.core import config, security

# from app.core.session import async_session
from app.core.session import SessionLocal
from app.models.model import Role, User


async def main() -> None:
    chars=string.digits
    print("Start initial data")
    async with SessionLocal() as session:
        result = await session.exec(
            select(User).where(User.username == config.settings.FIRST_SUPERUSER_EMAIL)
        )
        user = result.one_or_none()
        if user is None:
            new_superuser = User(
                username=config.settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=security.get_password_hash(
                    config.settings.FIRST_SUPERUSER_PASSWORD
                ),
                nik=''.join(random.choice(chars) for i in range(16)),
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

        print("Initial data created")


if __name__ == "__main__":
    asyncio.run(main())
