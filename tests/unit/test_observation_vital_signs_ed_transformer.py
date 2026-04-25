"""
Testes do transformador de ObservationVitalSignsED.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.observation_vital_signs_ed_transformer import (
    ObservationVitalSignsEDTransformationError,
    ObservationVitalSignsEDTransformer,
)


def test_transform_observation_vital_signs_ed_with_full_payload() -> None:
    """
    Deve transformar uma ObservationVitalSignsED completa consolidando os primeiros valores úteis.
    """

    transformer = ObservationVitalSignsEDTransformer()
    result = transformer.transform(
        {
            "id": "obs-vital-ed-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "partOf": [{"reference": "Procedure/proc-1"}],
            "code": {
                "coding": [
                    {"code": "", "system": "", "display": ""},
                    {
                        "code": "85354-9",
                        "system": "http://loinc.org",
                        "display": "Blood pressure panel",
                    },
                ]
            },
            "category": [
                {
                    "coding": [
                        {"code": "", "system": "", "display": ""},
                        {
                            "code": "vital-signs",
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "display": "Vital Signs",
                        },
                    ]
                }
            ],
            "effectiveDateTime": "2024-01-01T08:00:00Z",
            "valueQuantity": {
                "value": 120,
                "unit": "mm[Hg]",
                "code": "mm[Hg]",
                "system": "http://unitsofmeasure.org",
            },
            "component": [
                {
                    "code": {
                        "coding": [
                            {"code": "", "system": "", "display": ""},
                            {
                                "code": "8480-6",
                                "system": "http://loinc.org",
                                "display": "Systolic blood pressure",
                            },
                        ]
                    },
                    "valueQuantity": {
                        "value": 120,
                        "unit": "mm[Hg]",
                        "code": "mm[Hg]",
                        "system": "http://unitsofmeasure.org",
                    },
                }
            ],
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result.observation_vital_signs_ed == {
        "id": "obs-vital-ed-1",
        "patient_id": "pat-1",
        "encounter_id": "enc-1",
        "procedure_id": "proc-1",
        "status": "final",
        "observation_code": "85354-9",
        "observation_code_display": "Blood pressure panel",
        "category_code": "vital-signs",
        "category_display": "Vital Signs",
        "effective_at": "2024-01-01T08:00:00Z",
        "value": "120",
        "value_unit": "mm[Hg]",
        "value_code": "mm[Hg]",
    }
    assert result.observation_vital_signs_ed_components == [
        {
            "observation_vital_signs_ed_id": "obs-vital-ed-1",
            "component_code": "8480-6",
            "component_code_display": "Systolic blood pressure",
            "value": "120",
            "value_unit": "mm[Hg]",
            "value_code": "mm[Hg]",
        }
    ]


def test_transform_observation_vital_signs_ed_with_multiple_components() -> None:
    """
    Deve montar uma linha para cada componente válido.
    """

    transformer = ObservationVitalSignsEDTransformer()
    result = transformer.transform(
        {
            "id": "obs-vital-ed-1",
            "resourceType": "Observation",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "partOf": [{"reference": "Procedure/proc-1"}],
            "code": {"coding": [{"code": "85354-9"}]},
            "category": {"coding": [{"code": "vital-signs"}]},
            "component": [
                {
                    "code": {"coding": [{"code": "8480-6", "display": "Systolic"}]},
                    "valueQuantity": {"value": 120, "unit": "mm[Hg]"},
                },
                {
                    "code": {"coding": [{"code": "8462-4", "display": "Diastolic"}]},
                    "valueQuantity": {"value": 80, "unit": "mm[Hg]"},
                },
            ],
        }
    )

    assert len(result.observation_vital_signs_ed_components) == 2
    assert result.observation_vital_signs_ed_components[0]["component_code"] == "8480-6"
    assert result.observation_vital_signs_ed_components[1]["component_code"] == "8462-4"


def test_transform_observation_vital_signs_ed_without_encounter() -> None:
    """
    Deve aceitar ObservationVitalSignsED sem `encounter`.
    """

    transformer = ObservationVitalSignsEDTransformer()
    result = transformer.transform(
        {
            "id": "obs-vital-ed-1",
            "resourceType": "Observation",
            "subject": {"reference": "Patient/pat-1"},
            "partOf": [{"reference": "Procedure/proc-1"}],
            "code": {"coding": [{"code": "85354-9"}]},
            "category": {"coding": [{"code": "vital-signs"}]},
        }
    )

    assert result.observation_vital_signs_ed["encounter_id"] is None


def test_transform_observation_vital_signs_ed_without_partof() -> None:
    """
    Deve aceitar ObservationVitalSignsED sem `partOf`.
    """

    transformer = ObservationVitalSignsEDTransformer()
    result = transformer.transform(
        {
            "id": "obs-vital-ed-1",
            "resourceType": "Observation",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "code": {"coding": [{"code": "85354-9"}]},
            "category": {"coding": [{"code": "vital-signs"}]},
        }
    )

    assert result.observation_vital_signs_ed["procedure_id"] is None


def test_transform_observation_vital_signs_ed_without_value_quantity() -> None:
    """
    Deve aceitar ObservationVitalSignsED sem `valueQuantity`.
    """

    transformer = ObservationVitalSignsEDTransformer()
    result = transformer.transform(
        {
            "id": "obs-vital-ed-1",
            "resourceType": "Observation",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "partOf": [{"reference": "Procedure/proc-1"}],
            "code": {"coding": [{"code": "85354-9"}]},
            "category": {"coding": [{"code": "vital-signs"}]},
        }
    )

    assert result.observation_vital_signs_ed["value"] is None
    assert result.observation_vital_signs_ed["value_unit"] is None
    assert result.observation_vital_signs_ed["value_code"] is None
    

def test_transform_observation_vital_signs_ed_without_component() -> None:
    """
    Deve aceitar ObservationVitalSignsED sem `component`.
    """

    transformer = ObservationVitalSignsEDTransformer()
    result = transformer.transform(
        {
            "id": "obs-vital-ed-1",
            "resourceType": "Observation",
            "subject": {"reference": "Patient/pat-1"},
            "encounter": {"reference": "Encounter/enc-1"},
            "partOf": [{"reference": "Procedure/proc-1"}],
            "code": {"coding": [{"code": "85354-9"}]},
            "category": {"coding": [{"code": "vital-signs"}]},
        }
    )

    assert result.observation_vital_signs_ed_components == []


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("encounter", "Patient/pat-1", "Tipo de referência inválido"),
        ("partOf", "Encounter/enc-1", "Tipo de referência inválido"),
    ],
)
def test_transform_observation_vital_signs_ed_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = ObservationVitalSignsEDTransformer()
    payload: dict[str, object] = {
        "id": "obs-vital-ed-1",
        "resourceType": "Observation",
        "subject": {"reference": "Patient/pat-1"},
        "encounter": {"reference": "Encounter/enc-1"},
        "partOf": [{"reference": "Procedure/proc-1"}],
        "code": {"coding": [{"code": "85354-9"}]},
        "category": {"coding": [{"code": "vital-signs"}]},
    }
    if field_name == "subject":
        payload[field_name] = {"reference": reference_value}
    elif field_name == "partOf":
        payload[field_name] = [{"reference": reference_value}]
    else:
        payload[field_name] = {"reference": reference_value}

    with pytest.raises(ObservationVitalSignsEDTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_observation_vital_signs_ed_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as estruturas simplificadas do ObservationVitalSignsED.
    """

    transformer = ObservationVitalSignsEDTransformer()
    result = transformer.transform(
        {
            "id": "obs-vital-ed-1",
            "resourceType": "Observation",
            "subject": {"reference": "Patient/pat-1"},
            "code": {"coding": [{"code": "85354-9"}]},
            "component": [{"code": {"coding": [{"code": "8480-6"}]}}],
        }
    )

    assert set(result.observation_vital_signs_ed.keys()) == {
        "id",
        "patient_id",
        "encounter_id",
        "procedure_id",
        "status",
        "observation_code",
        "observation_code_display",
        "category_code",
        "category_display",
        "effective_at",
        "value",
        "value_unit",
        "value_code",
    }
    assert set(result.observation_vital_signs_ed_components[0].keys()) == {
        "observation_vital_signs_ed_id",
        "component_code",
        "component_code_display",
        "value",
        "value_unit",
        "value_code",
    }
