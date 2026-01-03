from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class VocabularyWord(Base):
    """Essential vocabulary words for learning English."""
    __tablename__ = "vocabulary_words"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    translation: Mapped[str] = mapped_column(String(100), nullable=False)
    phonetic: Mapped[str] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    example_sentence: Mapped[str] = mapped_column(Text, nullable=True)
    example_translation: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Relationships
    student_words: Mapped[list["StudentVocabulary"]] = relationship(back_populates="word")


class StudentVocabulary(Base):
    """Track which words each student has learned."""
    __tablename__ = "student_vocabulary"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    word_id: Mapped[int] = mapped_column(ForeignKey("vocabulary_words.id"), nullable=False)
    
    # Learning status
    times_seen: Mapped[int] = mapped_column(Integer, default=0)
    times_correct: Mapped[int] = mapped_column(Integer, default=0)
    mastery_level: Mapped[int] = mapped_column(Integer, default=0)  # 0-5 (0=new, 5=mastered)
    last_practiced: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    next_review: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_learned: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    student: Mapped["Student"] = relationship(back_populates="vocabulary")
    word: Mapped["VocabularyWord"] = relationship(back_populates="student_words")


# Vocabulary categories for Pre A1 level
VOCABULARY_CATEGORIES = [
    {"code": "GREETINGS", "name": "Saludos", "order": 1},
    {"code": "NUMBERS", "name": "Números", "order": 2},
    {"code": "COLORS", "name": "Colores", "order": 3},
    {"code": "FAMILY", "name": "Familia", "order": 4},
    {"code": "PRONOUNS", "name": "Pronombres", "order": 5},
    {"code": "ACTIONS", "name": "Verbos básicos", "order": 6},
    {"code": "FOOD", "name": "Comida y bebida", "order": 7},
    {"code": "BODY", "name": "Cuerpo humano", "order": 8},
    {"code": "CLOTHES", "name": "Ropa", "order": 9},
    {"code": "HOUSE", "name": "Casa", "order": 10},
    {"code": "TIME", "name": "Tiempo", "order": 11},
    {"code": "PLACES", "name": "Lugares", "order": 12},
    {"code": "ADJECTIVES", "name": "Adjetivos", "order": 13},
    {"code": "QUESTIONS", "name": "Preguntas", "order": 14},
    {"code": "ANIMALS", "name": "Animales", "order": 15},
]
