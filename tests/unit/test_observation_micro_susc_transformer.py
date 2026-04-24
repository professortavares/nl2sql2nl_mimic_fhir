"""
Testes do transformador de ObservationMicroSusc.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.observation_micro_susc_transformer import (
    ObservationMicroSuscTransformationError,
    ObservationMicroSuscTransformer,
)


def test_transform_observation_micro_susc_with_full_payload() -> None:
    """
    Deve transformar uma ObservationMicroSusc completa consolidando os primeiros valores úteis.
    """

    transformer = ObservationMicroSuscTransformer()
    result = transformer.transform(
        {
            "id": "obs-susc-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "derivedFrom": [
                {"reference": ""},
                {"reference": "Observation/obs-org-1"},
            ],
            "code": {
                "coding": [
                    {"code": "", "system": "", "display": ""},
                    {
                        "code": "ant-1",
                        "system": "http://mimic.mit.edu/fhir/mimic/CodeSystem/antibiotic",
                        "display": "Vancomycin",
                    },
                ]
            },
            "category": [
                {
                    "coding": [
                        {
                            "code": "microbiology",
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "display": "Microbiology",
                        }
                    ]
                }
            ],
            "effectiveDateTime": "2024-01-01T08:00:00Z",
            "identifier": [{"value": "susc-id-1"}],
            "valueCodeableConcept": {
                "coding": [
                    {
                        "code": "S",
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                        "display": "Susceptible",
                    }
                ]
            },
            "extension": [
                {"url": "ignored", "valueQuantity": {"value": 1, "comparator": "<"}},
                {
                    "url": "http://mimic.mit.edu/fhir/mimic/StructureDefinition/dilution-details",
                    "valueQuantity": {"value": 2, "comparator": ">="},
                },
            ],
            "note": [{"text": "Isolado com leitura em disco."}],
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result == {
        "id": "obs-susc-1",
        "patient_id": "pat-1",
        "derived_from_observation_micro_org_id": "obs-org-1",
        "status": "final",
        "antibiotic_code": "ant-1",
        "antibiotic_code_system": "http://mimic.mit.edu/fhir/mimic/CodeSystem/antibiotic",
        "antibiotic_code_display": "Vancomycin",
        "category_code": "microbiology",
        "category_system": "http://terminology.hl7.org/CodeSystem/observation-category",
        "category_display": "Microbiology",
        "effective_at": "2024-01-01T08:00:00Z",
        "identifier": "susc-id-1",
        "interpretation_code": "S",
        "interpretation_system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
        "interpretation_display": "Susceptible",
        "dilution_value": "2",
        "dilution_comparator": ">=",
        "note": "Isolado com leitura em disco.",
    }


def test_transform_observation_micro_susc_without_derived_from() -> None:
    """
    Deve aceitar ObservationMicroSusc sem `derivedFrom`.
    """

    transformer = ObservationMicroSuscTransformer()
    result = transformer.transform(
        {
            "id": "obs-susc-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "code": {"coding": [{"code": "ant-1"}]},
            "category": {"coding": [{"code": "microbiology"}]},
        }
    )

    assert result["derived_from_observation_micro_org_id"] is None


def test_transform_observation_micro_susc_without_value_codeable_concept() -> None:
    """
    Deve aceitar ObservationMicroSusc sem `valueCodeableConcept`.
    """

    transformer = ObservationMicroSuscTransformer()
    result = transformer.transform(
        {
            "id": "obs-susc-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "derivedFrom": [{"reference": "Observation/obs-org-1"}],
            "code": {"coding": [{"code": "ant-1"}]},
            "category": {"coding": [{"code": "microbiology"}]},
        }
    )

    assert result["interpretation_code"] is None
    assert result["interpretation_system"] is None
    assert result["interpretation_display"] is None


def test_transform_observation_micro_susc_without_dilution_extension() -> None:
    """
    Deve aceitar ObservationMicroSusc sem extensão de diluição.
    """

    transformer = ObservationMicroSuscTransformer()
    result = transformer.transform(
        {
            "id": "obs-susc-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "derivedFrom": [{"reference": "Observation/obs-org-1"}],
            "code": {"coding": [{"code": "ant-1"}]},
            "category": {"coding": [{"code": "microbiology"}]},
            "valueCodeableConcept": {"coding": [{"code": "S"}]},
        }
    )

    assert result["dilution_value"] is None
    assert result["dilution_comparator"] is None


def test_transform_observation_micro_susc_without_note() -> None:
    """
    Deve aceitar ObservationMicroSusc sem `note`.
    """

    transformer = ObservationMicroSuscTransformer()
    result = transformer.transform(
        {
            "id": "obs-susc-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "derivedFrom": [{"reference": "Observation/obs-org-1"}],
            "code": {"coding": [{"code": "ant-1"}]},
            "category": {"coding": [{"code": "microbiology"}]},
        }
    )

    assert result["note"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("derivedFrom", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_observation_micro_susc_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais.
    """

    transformer = ObservationMicroSuscTransformer()
    payload: dict[str, object] = {
        "id": "obs-susc-1",
        "resourceType": "Observation",
        "status": "final",
        "subject": {"reference": "Patient/pat-1"},
        "derivedFrom": [{"reference": "Observation/obs-org-1"}],
        "code": {"coding": [{"code": "ant-1"}]},
        "category": {"coding": [{"code": "microbiology"}]},
    }
    if field_name == "subject":
        payload[field_name] = {"reference": reference_value}
    else:
        payload[field_name] = [{"reference": reference_value}]

    with pytest.raises(ObservationMicroSuscTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_observation_micro_susc_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as estruturas simplificadas do ObservationMicroSusc.
    """

    transformer = ObservationMicroSuscTransformer()
    result = transformer.transform(
        {
            "id": "obs-susc-1",
            "resourceType": "Observation",
            "subject": {"reference": "Patient/pat-1"},
            "derivedFrom": [{"reference": "Observation/obs-org-1"}],
            "code": {"coding": [{"code": "ant-1"}]},
            "category": {"coding": [{"code": "microbiology"}]},
        }
    )

    assert set(result.keys()) == {
        "id",
        "patient_id",
        "derived_from_observation_micro_org_id",
        "status",
        "antibiotic_code",
        "antibiotic_code_system",
        "antibiotic_code_display",
        "category_code",
        "category_system",
        "category_display",
        "effective_at",
        "identifier",
        "interpretation_code",
        "interpretation_system",
        "interpretation_display",
        "dilution_value",
        "dilution_comparator",
        "note",
    }
