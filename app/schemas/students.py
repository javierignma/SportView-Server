from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class StudentProgressAverage(SQLModel, table=False):
    technique_avg: float
    physique_avg: float
    combat_iq_avg: float