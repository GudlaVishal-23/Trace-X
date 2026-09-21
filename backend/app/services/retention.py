import logging
from datetime import datetime, timezone, timedelta
from backend.app.database import SessionLocal
from backend.app.models import VehicleEvent, Alert

logger = logging.getLogger("tracex.retention")

def purge_expired_records(days_retention: int = 30) -> int:
    """
    Automated Record Expiration Policy (DPDP Act 2023 & SIH Master Document Section 36).
    Purges structured events older than days_retention (default 30 days) to enforce
    data minimization and prevent indefinite citizen tracking data retention.
    """
    db = SessionLocal()
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_retention)
        
        # Purge non-flagged historical events older than cutoff
        deleted_count = db.query(VehicleEvent).filter(
            VehicleEvent.timestamp < cutoff_date
        ).delete(synchronize_session=False)

        # Purge dismissed or resolved alerts older than cutoff
        db.query(Alert).filter(
            Alert.timestamp < cutoff_date,
            Alert.status.in_(["DISMISSED", "RESOLVED"])
        ).delete(synchronize_session=False)

        db.commit()
        if deleted_count > 0:
            logger.info(f"Retention Cleanup: Purged {deleted_count} vehicle events older than {days_retention} days.")
        return deleted_count
    except Exception as e:
        db.rollback()
        logger.error(f"Retention policy cleanup failed: {e}", exc_info=True)
        return 0
    finally:
        db.close()
