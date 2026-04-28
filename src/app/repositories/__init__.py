"""
Repositórios da aplicação de timeline clínica.
"""

from __future__ import annotations

from src.app.repositories.clinical_events_repository import ClinicalEventsRepository
from src.app.repositories.emergency_department_repository import EmergencyDepartmentRepository
from src.app.repositories.encounter_repository import EncounterRepository
from src.app.repositories.general_hospital_repository import GeneralHospitalRepository
from src.app.repositories.icu_repository import IcuRepository
from src.app.repositories.patient_repository import PatientRepository

__all__ = [
    "PatientRepository",
    "EncounterRepository",
    "GeneralHospitalRepository",
    "EmergencyDepartmentRepository",
    "IcuRepository",
    "ClinicalEventsRepository",
]
