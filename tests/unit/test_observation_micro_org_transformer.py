"""
Testes do transformador de ObservationMicroOrg.
"""

from __future__ import annotations

import pytest

from src.ingestion.transformers.observation_micro_org_transformer import (
    ObservationMicroOrgTransformationError,
    ObservationMicroOrgTransformer,
)


def test_transform_observation_micro_org_with_full_payload() -> None:
    """
    Deve transformar uma ObservationMicroOrg completa consolidando os primeiros valores úteis.
    """

    transformer = ObservationMicroOrgTransformer()
    result = transformer.transform(
        {
            "id": "obs-org-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "derivedFrom": [
                {"reference": ""},
                {"reference": "Observation/obs-micro-test-1"},
            ],
            "hasMember": [
                {"reference": "Observation/member-1"},
                {"reference": "Observation/member-2"},
            ],
            "code": {
                "coding": [
                    {"code": "", "system": "", "display": ""},
                    {
                        "code": "org-1",
                        "system": "http://mimic.mit.edu/fhir/mimic/CodeSystem/micro-organism",
                        "display": "Staphylococcus aureus",
                    },
                ]
            },
            "category": [
                {
                    "coding": [
                        {"code": "", "system": "", "display": ""},
                    ]
                },
                {
                    "coding": [
                        {
                            "code": "microbiology",
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "display": "Microbiology",
                        }
                    ]
                },
            ],
            "effectiveDateTime": "2024-01-01T08:00:00Z",
            "valueString": "Staphylococcus aureus",
            "meta": {"profile": ["ignored"]},
        }
    )

    assert result.observation_micro_org == {
        "id": "obs-org-1",
        "patient_id": "pat-1",
        "derived_from_observation_micro_test_id": "obs-micro-test-1",
        "status": "final",
        "organism_code": "org-1",
        "organism_code_system": "http://mimic.mit.edu/fhir/mimic/CodeSystem/micro-organism",
        "organism_code_display": "Staphylococcus aureus",
        "category_code": "microbiology",
        "category_system": "http://terminology.hl7.org/CodeSystem/observation-category",
        "category_display": "Microbiology",
        "effective_at": "2024-01-01T08:00:00Z",
        "value_string": "Staphylococcus aureus",
    }
    assert result.observation_micro_org_has_member == [
        {
            "observation_micro_org_id": "obs-org-1",
            "member_observation_id": "member-1",
        },
        {
            "observation_micro_org_id": "obs-org-1",
            "member_observation_id": "member-2",
        },
    ]


def test_transform_observation_micro_org_without_derived_from() -> None:
    """
    Deve aceitar ObservationMicroOrg sem `derivedFrom`.
    """

    transformer = ObservationMicroOrgTransformer()
    result = transformer.transform(
        {
            "id": "obs-org-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "code": {"coding": [{"code": "org-1"}]},
            "category": {"coding": [{"code": "microbiology"}]},
        }
    )

    assert result.observation_micro_org["derived_from_observation_micro_test_id"] is None
    assert result.observation_micro_org_has_member == []


def test_transform_observation_micro_org_without_has_member() -> None:
    """
    Deve aceitar ObservationMicroOrg sem `hasMember`.
    """

    transformer = ObservationMicroOrgTransformer()
    result = transformer.transform(
        {
            "id": "obs-org-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "derivedFrom": [{"reference": "Observation/obs-micro-test-1"}],
            "code": {"coding": [{"code": "org-1"}]},
            "category": {"coding": [{"code": "microbiology"}]},
        }
    )

    assert result.observation_micro_org_has_member == []


def test_transform_observation_micro_org_without_value_string() -> None:
    """
    Deve aceitar ObservationMicroOrg sem `valueString`.
    """

    transformer = ObservationMicroOrgTransformer()
    result = transformer.transform(
        {
            "id": "obs-org-1",
            "resourceType": "Observation",
            "status": "final",
            "subject": {"reference": "Patient/pat-1"},
            "derivedFrom": [{"reference": "Observation/obs-micro-test-1"}],
            "code": {"coding": [{"code": "org-1"}]},
            "category": {"coding": [{"code": "microbiology"}]},
        }
    )

    assert result.observation_micro_org["value_string"] is None


@pytest.mark.parametrize(
    "field_name, reference_value, expected_message",
    [
        ("subject", "Encounter/enc-1", "Tipo de referência inválido"),
        ("derivedFrom", "Patient/pat-1", "Tipo de referência inválido"),
        ("hasMember", "Patient/pat-1", "Tipo de referência inválido"),
    ],
)
def test_transform_observation_micro_org_rejects_invalid_references(
    field_name: str,
    reference_value: str,
    expected_message: str,
) -> None:
    """
    Deve rejeitar referências FHIR inválidas nos vínculos principais e auxiliares.
    """

    transformer = ObservationMicroOrgTransformer()
    payload: dict[str, object] = {
        "id": "obs-org-1",
        "resourceType": "Observation",
        "status": "final",
        "subject": {"reference": "Patient/pat-1"},
        "derivedFrom": [{"reference": "Observation/obs-micro-test-1"}],
        "hasMember": [{"reference": "Observation/member-1"}],
        "code": {"coding": [{"code": "org-1"}]},
        "category": {"coding": [{"code": "microbiology"}]},
    }
    if field_name == "subject":
        payload[field_name] = {"reference": reference_value}
    elif field_name == "derivedFrom":
        payload[field_name] = [{"reference": reference_value}]
    else:
        payload[field_name] = [{"reference": reference_value}]

    with pytest.raises(ObservationMicroOrgTransformationError, match=expected_message):
        transformer.transform(payload)


def test_transform_observation_micro_org_returns_only_simplified_columns() -> None:
    """
    Deve retornar apenas as estruturas simplificadas do ObservationMicroOrg.
    """

    transformer = ObservationMicroOrgTransformer()
    result = transformer.transform(
        {
            "id": "obs-org-1",
            "resourceType": "Observation",
            "subject": {"reference": "Patient/pat-1"},
            "derivedFrom": [{"reference": "Observation/obs-micro-test-1"}],
            "code": {"coding": [{"code": "org-1"}]},
            "category": {"coding": [{"code": "microbiology"}]},
        }
    )

    assert set(result.observation_micro_org.keys()) == {
        "id",
        "patient_id",
        "derived_from_observation_micro_test_id",
        "status",
        "organism_code",
        "organism_code_system",
        "organism_code_display",
        "category_code",
        "category_system",
        "category_display",
        "effective_at",
        "value_string",
    }
    assert result.observation_micro_org_has_member == []
