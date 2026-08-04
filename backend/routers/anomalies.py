"""
Anomaly listing and detail router.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..dependencies import get_dataset_service
from ..models.responses import (
    AnomalyResponse,
    AnomalyListResponse,
    AnomalySummary,
    AnomalyDetailResponse,
    RootCauseResponse,
    DriverResponse,
    CorrelationResponse,
    ChangePointResponse,
    ExplanationResponse as ExplanationResponseModel,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Anomalies"])


@router.get("/datasets/{dataset_id}/anomalies", response_model=AnomalyListResponse)
async def list_anomalies(
    dataset_id: str,
    severity_min: float = Query(0.0, ge=0, le=1),
    anomaly_type: Optional[str] = None,
    metric: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
):
    """List anomalies for a dataset with filters."""
    dataset_svc = get_dataset_service()

    # Verify dataset exists
    dataset = dataset_svc.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    result = dataset_svc.get_anomalies(
        dataset_id=dataset_id,
        severity_min=severity_min,
        anomaly_type=anomaly_type,
        metric=metric,
        page=page,
        per_page=per_page,
    )

    anomalies = [
        AnomalyResponse(
            id=a["id"],
            dataset_id=a["dataset_id"],
            timestamp=a.get("timestamp"),
            metric=a["metric"],
            value=a["value"],
            expected_min=a.get("expected_min"),
            expected_max=a.get("expected_max"),
            anomaly_type=a["anomaly_type"],
            severity=a["severity"],
            confidence=a["confidence"],
            dimensions=a.get("dimensions", {}),
        )
        for a in result["anomalies"]
    ]

    summary_data = result.get("summary", {})

    return AnomalyListResponse(
        anomalies=anomalies,
        summary=AnomalySummary(
            total_anomalies=summary_data.get("total_anomalies", 0),
            avg_severity=summary_data.get("avg_severity", 0),
            by_type=summary_data.get("by_type", {}),
            by_severity_level=summary_data.get("by_severity_level", {}),
        ),
        total=result["total"],
        page=result["page"],
        per_page=result["per_page"],
    )


@router.get("/anomalies/{anomaly_id}", response_model=AnomalyDetailResponse)
async def get_anomaly_detail(anomaly_id: str):
    """Get full anomaly detail with root cause and explanation."""
    dataset_svc = get_dataset_service()
    result = dataset_svc.get_anomaly_detail(anomaly_id)

    if not result:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    # Build anomaly response
    a = result["anomaly"]
    anomaly_resp = AnomalyResponse(
        id=a["id"],
        dataset_id=a["dataset_id"],
        timestamp=a.get("timestamp"),
        metric=a["metric"],
        value=a["value"],
        expected_min=a.get("expected_min"),
        expected_max=a.get("expected_max"),
        anomaly_type=a["anomaly_type"],
        severity=a["severity"],
        confidence=a["confidence"],
        dimensions=a.get("dimensions", {}),
    )

    # Build root cause response
    root_cause_resp = None
    if "root_cause" in result and result["root_cause"]:
        rc = result["root_cause"]
        root_cause_resp = RootCauseResponse(
            primary_drivers=[
                DriverResponse(
                    segment=d.get("segment", "Unknown"),
                    contribution=d.get("contribution", 0),
                    baseline_ratio=d.get("baseline_ratio", 1.0),
                )
                for d in rc.get("primary_drivers", [])
            ],
            correlations=[
                CorrelationResponse(
                    metric=c.get("metric", ""),
                    coefficient=c.get("coefficient", 0),
                    p_value=c.get("p_value"),
                    lag_hours=c.get("lag_hours"),
                )
                for c in rc.get("correlations", [])
            ],
            change_point=(
                ChangePointResponse(
                    detected_at=str(rc["change_point"].get("detected_at", "")),
                    confidence=rc["change_point"].get("confidence", 0),
                    before_mean=rc["change_point"].get("before_mean", 0),
                    after_mean=rc["change_point"].get("after_mean", 0),
                    change_magnitude=rc["change_point"].get("change_magnitude", 0),
                )
                if rc.get("change_point")
                else None
            ),
            hypothesis=rc.get("hypothesis", ""),
            confidence=rc.get("confidence", 0),
            methods_used=rc.get("methods_used", []),
        )

    # Build explanation response
    explanation_resp = None
    if "explanation" in result and result["explanation"]:
        exp = result["explanation"]
        explanation_resp = ExplanationResponseModel(
            text=exp.get("text", ""),
            summary=exp.get("summary", ""),
            recommendations=exp.get("recommendations", []),
            confidence=exp.get("confidence", 0),
            evidence_citations=exp.get("evidence_citations", []),
            llm_model=exp.get("llm_model"),
            used_fallback=exp.get("used_fallback", False),
            generated_at=exp.get("generated_at"),
        )

    return AnomalyDetailResponse(
        anomaly=anomaly_resp,
        root_cause=root_cause_resp,
        explanation=explanation_resp,
    )
