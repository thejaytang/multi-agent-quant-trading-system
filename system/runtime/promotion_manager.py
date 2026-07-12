from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any
from uuid import uuid4

from system.schemas._validation import ValidationError, has_required_metadata, utc_now
from system.schemas.promotion_schema import PromotionCandidateSchema

RISK_REVIEW_ASSET_TYPES = {"strategy", "capital_update", "portfolio_update", "ledger_update"}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----"),
    re.compile(r"(?i)(api[_-]?key|secret|token)[ \t]*[:=][ \t]*['\"]?[A-Za-z0-9_\-]{16,}"),
)


class PromotionManager:
    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or Path.cwd()).resolve()

    def create_promotion_candidate(
        self,
        asset_type: str,
        source_workspace_path: str | Path,
        target_persistent_path: str | Path,
        created_by_agent: str,
        workflow_id: str,
        metadata: dict[str, Any],
    ) -> PromotionCandidateSchema:
        candidate = PromotionCandidateSchema(
            candidate_id=f"pc_{uuid4().hex[:12]}",
            asset_type=asset_type,
            source_workspace_path=str(source_workspace_path),
            target_persistent_path=str(target_persistent_path),
            created_by_agent=created_by_agent,
            workflow_id=workflow_id,
            created_at=utc_now(),
            metadata=metadata,
            leader_review_required=True,
            risk_review_required=asset_type in RISK_REVIEW_ASSET_TYPES,
            status="created",
            review_notes=[],
        ).validate()
        return candidate

    def validate_candidate(self, candidate: PromotionCandidateSchema) -> bool:
        candidate.validate()
        source = self._resolve(candidate.source_workspace_path)
        target = self._resolve(candidate.target_persistent_path)
        if not self._is_under(source, self.root / "workspace"):
            raise ValidationError("source_workspace_path must be under workspace")
        if not self._is_under(target, self.root / "persistent"):
            raise ValidationError("target_persistent_path must be under persistent")
        if not source.exists():
            raise ValidationError("source_workspace_path does not exist")
        if not has_required_metadata(candidate.metadata):
            raise ValidationError("metadata must include workflow_id, source, created_at, created_by")
        self._check_no_secrets(source)
        if candidate.asset_type == "strategy":
            self._require_file(source, "risk.yaml")
        if candidate.asset_type == "experiment":
            for file_name in (
                "data_version.json",
                "code_version.txt",
                "params.json",
                "cost_model.json",
                "slippage_model.json",
                "results.json",
            ):
                self._require_file(source, file_name)
        return True

    def request_leader_review(
        self,
        candidate: PromotionCandidateSchema,
        reviewer_agent: str = "LeaderAgent",
        approved: bool = True,
        note: str = "leader review completed",
    ) -> PromotionCandidateSchema:
        if reviewer_agent != "LeaderAgent":
            raise PermissionError("Only LeaderAgent can perform leader review")
        self.validate_candidate(candidate)
        candidate.review_notes.append(note)
        candidate.status = "leader_approved" if approved else "leader_rejected"
        return candidate

    def request_risk_review_if_needed(
        self,
        candidate: PromotionCandidateSchema,
        reviewer_agent: str = "RiskControlAgent",
        approved: bool = True,
        note: str = "risk review completed",
    ) -> PromotionCandidateSchema:
        if not candidate.risk_review_required:
            candidate.review_notes.append("risk review not required")
            return candidate
        if reviewer_agent != "RiskControlAgent":
            raise PermissionError("Only RiskControlAgent can perform risk review")
        if candidate.status not in {"leader_approved", "risk_rejected"}:
            raise ValidationError("leader approval is required before risk review")
        candidate.review_notes.append(note)
        candidate.status = "risk_approved" if approved else "risk_rejected"
        return candidate

    def promote_to_persistent(self, candidate: PromotionCandidateSchema) -> Path:
        self.validate_candidate(candidate)
        if candidate.status == "risk_rejected":
            raise ValidationError("RiskControlAgent rejection cannot be overridden")
        if candidate.risk_review_required and candidate.status != "risk_approved":
            raise ValidationError("risk review is required before promotion")
        if not candidate.risk_review_required and candidate.status != "leader_approved":
            raise ValidationError("leader review is required before promotion")
        source = self._resolve(candidate.source_workspace_path)
        target = self._resolve(candidate.target_persistent_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
        candidate.status = "promoted"
        self.update_registry_or_index(candidate)
        self.log_promotion_decision(candidate, "promoted")
        return target

    def update_registry_or_index(self, candidate: PromotionCandidateSchema) -> None:
        if candidate.asset_type != "strategy":
            return
        index_path = self.root / "persistent" / "strategies" / "strategy_index.json"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        if index_path.exists():
            data = json.loads(index_path.read_text(encoding="utf-8"))
        else:
            data = {"strategies": []}
        entry = {
            "candidate_id": candidate.candidate_id,
            "target": candidate.target_persistent_path,
            "workflow_id": candidate.workflow_id,
            "updated_at": utc_now(),
        }
        data.setdefault("strategies", []).append(entry)
        index_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def log_promotion_decision(self, candidate: PromotionCandidateSchema, decision: str) -> None:
        log_dir = self.root / "logs" / "promotion_decisions"
        log_dir.mkdir(parents=True, exist_ok=True)
        event = {
            "candidate_id": candidate.candidate_id,
            "asset_type": candidate.asset_type,
            "decision": decision,
            "status": candidate.status,
            "workflow_id": candidate.workflow_id,
            "created_at": utc_now(),
            "created_by": "LeaderAgent",
            "source": "system.runtime.promotion_manager",
        }
        with (log_dir / "promotion_decisions.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event) + "\n")
        decision_log = self.root / "persistent" / "decisions" / "decision_log.jsonl"
        decision_log.parent.mkdir(parents=True, exist_ok=True)
        with decision_log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event) + "\n")

    def _resolve(self, path: str | Path) -> Path:
        path = Path(path)
        return path if path.is_absolute() else (self.root / path).resolve()

    @staticmethod
    def _is_under(path: Path, parent: Path) -> bool:
        try:
            path.resolve().relative_to(parent.resolve())
            return True
        except ValueError:
            return False

    @staticmethod
    def _require_file(base: Path, file_name: str) -> None:
        target = base / file_name if base.is_dir() else base.parent / file_name
        if not target.exists():
            raise ValidationError(f"required file missing: {file_name}")

    @staticmethod
    def _check_no_secrets(path: Path) -> None:
        files = path.rglob("*") if path.is_dir() else [path]
        for file_path in files:
            if not file_path.is_file() or file_path.suffix in {".pyc", ".png", ".jpg", ".jpeg"}:
                continue
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    raise ValidationError(f"possible secret found in {file_path}")
