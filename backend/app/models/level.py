from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Level(Base):
    __tablename__ = "levels"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Relationships
    students: Mapped[list["Student"]] = relationship(back_populates="current_level")
    student_skills: Mapped[list["StudentSkill"]] = relationship(back_populates="level")
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="level")


# Seed data for levels
LEVEL_SEED_DATA = [
    {"code": "PRE_A1", "name": "Pre A1 - Principiante", "order": 0,
     "description": "Nivel inicial. Aprende palabras básicas, saludos y frases muy simples."},
    {"code": "A1", "name": "A1 - Elemental", "order": 1,
     "description": "Puede usar expresiones cotidianas y frases básicas para satisfacer necesidades concretas."},
    {"code": "A2", "name": "A2 - Pre-intermedio", "order": 2,
     "description": "Puede comunicarse en tareas simples y describir aspectos de su entorno."},
    {"code": "B1", "name": "B1 - Intermedio", "order": 3,
     "description": "Puede desenvolverse en situaciones de viaje y describir experiencias y eventos."},
    {"code": "B2", "name": "B2 - Intermedio Alto", "order": 4,
     "description": "Puede interactuar con fluidez con hablantes nativos sin esfuerzo."},
    {"code": "C1", "name": "C1 - Avanzado", "order": 5,
     "description": "Puede expresarse con fluidez y espontaneidad, uso flexible del idioma."},
]
