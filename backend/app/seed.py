"""
Script to seed the database with initial data.
Run with: python -m app.seed
"""
import asyncio
import logging
from app.database import AsyncSessionLocal, init_db
from app.models.level import Level, LEVEL_SEED_DATA
from app.models.skill import Skill, SKILL_SEED_DATA
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_levels(db):
    """Seed levels table."""
    for level_data in LEVEL_SEED_DATA:
        result = await db.execute(
            select(Level).where(Level.code == level_data["code"])
        )
        if not result.scalar_one_or_none():
            level = Level(**level_data)
            db.add(level)
            logger.info(f"Created level: {level_data['name']}")
    await db.commit()


async def seed_skills(db):
    """Seed skills table."""
    for skill_data in SKILL_SEED_DATA:
        result = await db.execute(
            select(Skill).where(Skill.code == skill_data["code"])
        )
        if not result.scalar_one_or_none():
            skill = Skill(**skill_data)
            db.add(skill)
            logger.info(f"Created skill: {skill_data['name']}")
    await db.commit()


async def main():
    logger.info("Initializing database...")
    await init_db()
    
    async with AsyncSessionLocal() as db:
        logger.info("Seeding levels...")
        await seed_levels(db)
        
        logger.info("Seeding skills...")
        await seed_skills(db)
    
    logger.info("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
