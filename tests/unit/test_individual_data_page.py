"""
Testes dos helpers da página de dados individuais.
"""

from __future__ import annotations

from src.app.pages.individual_data import _format_datetime_display, _group_medication_events


def test_format_datetime_display_normalizes_iso_values() -> None:
    """Deve converter datas ISO em um formato legível."""

    assert _format_datetime_display("2024-01-01T12:30:00") == "2024-01-01 12:30"
    assert _format_datetime_display("2024-01-01") == "2024-01-01"
    assert _format_datetime_display(None) is None


def test_group_medication_events_collapses_rows_by_medication_and_request() -> None:
    """Deve agrupar linhas repetidas por medicação/prescrição."""

    grouped = _group_medication_events(
        [
            {
                "medication_request_id": "mr-1",
                "validity_start": "2024-01-01T08:00:00",
                "validity_end": "2024-01-01T20:00:00",
                "medication_name": "Morphine",
                "frequency_code": "ONCE",
                "request_status": "completed",
                "request_intent": "order",
                "request_identifier": "req-1",
                "medication_administration_id": "ma-1",
                "effective_at": "2024-01-01T10:00:00",
                "dose_value": "2",
                "dose_unit": "mg",
                "status": "completed",
            },
            {
                "medication_request_id": "mr-1",
                "validity_start": "2024-01-01T08:00:00",
                "validity_end": "2024-01-01T20:00:00",
                "medication_name": "Morphine",
                "frequency_code": "ONCE",
                "request_status": "completed",
                "request_intent": "order",
                "request_identifier": "req-1",
                "medication_administration_id": "ma-2",
                "effective_at": "2024-01-01T12:00:00",
                "dose_value": "2",
                "dose_unit": "mg",
                "status": "completed",
            },
        ]
    )

    assert grouped == [
        {
            "medication_name": "Morphine",
            "prescriptions": [
                {
                    "medication_request_id": "mr-1",
                    "validity_start": "2024-01-01T08:00:00",
                    "validity_end": "2024-01-01T20:00:00",
                    "frequency_code": "ONCE",
                    "request_status": "completed",
                    "request_intent": "order",
                    "request_identifier": "req-1",
                    "administrations": [
                        {
                            "id": "ma-1",
                            "effective_at": "2024-01-01T10:00:00",
                            "dose_value": "2",
                            "dose_unit": "mg",
                            "status": "completed",
                        },
                        {
                            "id": "ma-2",
                            "effective_at": "2024-01-01T12:00:00",
                            "dose_value": "2",
                            "dose_unit": "mg",
                            "status": "completed",
                        },
                    ],
                }
            ],
        }
    ]
