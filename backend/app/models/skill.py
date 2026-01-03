from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Skill(Base):
    __tablename__ = "skills"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # Relationships
    student_skills: Mapped[list["StudentSkill"]] = relationship(back_populates="skill")


# Seed data for skills
SKILL_SEED_DATA = [
    {"code": "SPEAKING", "name": "Speaking", "icon": "mic",
     "description": "Habilidad para comunicarse oralmente en inglés."},
    {"code": "LISTENING", "name": "Listening", "icon": "headphones",
     "description": "Habilidad para comprender el inglés hablado."},
    {"code": "READING", "name": "Reading", "icon": "book-open",
     "description": "Habilidad para leer y comprender textos en inglés."},
    {"code": "WRITING", "name": "Writing", "icon": "pencil",
     "description": "Habilidad para escribir en inglés."},
    {"code": "VOCABULARY", "name": "Vocabulary", "icon": "library",
     "description": "Conocimiento de palabras y expresiones en inglés."},
    {"code": "GRAMMAR", "name": "Grammar", "icon": "brackets",
     "description": "Conocimiento de las reglas gramaticales del inglés."},
]
