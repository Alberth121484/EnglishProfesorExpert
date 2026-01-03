from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Assessment(Base):
    __tablename__ = "assessments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    # Types: "PLACEMENT" (initial), "PROGRESS" (periodic), "LEVEL_UP" (promotion test)
    
    level_before_id: Mapped[int | None] = mapped_column(ForeignKey("levels.id"), nullable=True)
    level_after_id: Mapped[int | None] = mapped_column(ForeignKey("levels.id"), nullable=True)
    
    score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100
    passed: Mapped[bool] = mapped_column(default=False)
    
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Example: {"speaking": 80, "listening": 75, "grammar": 70, "vocabulary": 85}
    
    taken_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    
    # Relationships
    student: Mapped["Student"] = relationship(back_populates="assessments")
    level_before: Mapped["Level"] = relationship(foreign_keys=[level_before_id])
    level_after: Mapped["Level"] = relationship(foreign_keys=[level_after_id])
