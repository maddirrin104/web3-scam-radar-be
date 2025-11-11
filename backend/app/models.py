from sqlalchemy import (
String, Integer, BigInteger, Boolean, DateTime, Text, ForeignKey, JSON, UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app.db import Base

class Rule(Base):
    __tablename__ = "rules"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(512))
    weight: Mapped[int] = mapped_column(Integer, default=10) # impact weight
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class PolicySnapshot(Base):
    __tablename__ = "policy_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    etag: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    payload: Mapped[dict] = mapped_column(JSON)


class DomainReputation(Base):
    __tablename__ = "domain_reputation"
    id: Mapped[int] = mapped_column(primary_key=True)
    domain: Mapped[str] = mapped_column(String(255), index=True)
    risk: Mapped[int] = mapped_column(Integer, default=0) # 0-100
    labels: Mapped[dict] = mapped_column(JSON, default=dict)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    __table_args__ = (UniqueConstraint('domain', name='uq_domain'),)


class ContractReputation(Base):
    __tablename__ = "contract_reputation"
    id: Mapped[int] = mapped_column(primary_key=True)
    chain_id: Mapped[int] = mapped_column(BigInteger, index=True)
    address: Mapped[str] = mapped_column(String(64), index=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    risk: Mapped[int] = mapped_column(Integer, default=0)
    labels: Mapped[dict] = mapped_column(JSON, default=dict)
    __table_args__ = (
        UniqueConstraint('chain_id','address', name='uq_chain_addr'),
        Index('ix_contract_combo', 'chain_id', 'address')
    )


class FourByteSelector(Base):
    __tablename__ = "fourbyte"
    id: Mapped[int] = mapped_column(primary_key=True)
    selector: Mapped[str] = mapped_column(String(10), index=True)
    signature: Mapped[str] = mapped_column(String(255))
    __table_args__ = (UniqueConstraint('selector', name='uq_selector'),)


class AlertLog(Base):
    __tablename__ = "alert_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    tab_domain: Mapped[str] = mapped_column(String(255))
    chain_id: Mapped[int] = mapped_column(BigInteger)
    contract: Mapped[str] = mapped_column(String(64))
    selector: Mapped[str] = mapped_column(String(10))
    risk: Mapped[int] = mapped_column(Integer)
    verdict: Mapped[str] = mapped_column(String(32)) # BLOCK/ALLOW/WARN
    reason: Mapped[str] = mapped_column(String(512))
    raw: Mapped[dict] = mapped_column(JSON)