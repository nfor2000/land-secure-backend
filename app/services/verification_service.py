from datetime import datetime
from typing import Optional
from sqlmodel import Session, select
from app.models.land_models import VerificationRequest, LandRegistry
from app.schemas.land_schemas import VerificationRequestCreate
from app.services.geometry_service import geometry
from app.core.database import engine
import logging

logger = logging.getLogger(__name__)


class SimpleVerifier:
    """Simple land verification logic"""

    def verify_land(
        self,
        db: Session,
        user_id: int,
        request: VerificationRequestCreate,
    ) -> VerificationRequest:
        """
        Verification flow:
        1. Search registry
        2. Check exact location match
        3. Check coordinate overlap
        4. Determine final status
        """

        logger.info(
            "Starting land verification | user_id=%s | town=%s | layout=%s | block=%s | plot=%s",
            user_id,
            request.town,
            request.layout,
            request.block_number,
            request.plot_number,
        )

        vr = VerificationRequest(
            user_id=user_id,
            submitted_town=request.town,
            submitted_layout=request.layout,
            submitted_block=request.block_number,
            submitted_plot=request.plot_number,
            submitted_coords=[{"lat": c.lat, "lng": c.lng} for c in request.coordinates],
            status="pending",
        )

        db.add(vr)
        db.commit()
        db.refresh(vr)

        try:
            registry = self._search_registry(request)

            if not registry:
                logger.info("No registry record found")
                vr.status = "failed"
                vr.message = "Land not found in registry"
                db.commit()
                return vr

            # 1️⃣ Exact location check
            location_match = (
                request.town.lower() == registry.town.lower()
                and request.layout.lower() == registry.layout.lower()
                and request.block_number == registry.block_number
                and request.plot_number == registry.plot_number
            )

            vr.location_match = location_match

            if not location_match:
                logger.warning(
                    "Location mismatch | registry_id=%s",
                    registry.id,
                )
                vr.status = "fraudulent"
                vr.is_fraud = True
                vr.fraud_reason = "Location information mismatch"
                vr.message = "Location does not match registry"
                db.commit()
                return vr

            # 2️⃣ Coordinate comparison
            submitted_points = geometry.points_to_list(vr.submitted_coords)
            official_points = geometry.points_to_list(registry.coordinates)

            coord_check = geometry.compare_polygons(
                submitted_points,
                official_points,
            )

            vr.coordinates_match = coord_check["match"]
            vr.overlap_score = coord_check["area_ratio"]
            vr.distance_meters = coord_check["distance_meters"]

            if coord_check["match"]:
                logger.info(
                    "Verification successful | registry_id=%s | overlap=%.2f",
                    registry.id,
                    coord_check["area_ratio"],
                )

                vr.status = "verified"
                vr.is_verified = True
                vr.message = "Land verification successful"

                vr.official_owner = registry.owner_name
                vr.official_coords = registry.coordinates
                vr.official_area = registry.area_square_meters
            else:
                logger.warning(
                    "Coordinate mismatch | registry_id=%s | distance=%.2fm",
                    registry.id,
                    coord_check["distance_meters"],
                )

                vr.status = "fraudulent"
                vr.is_fraud = True
                vr.fraud_reason = (
                    f"Coordinates mismatch "
                    f"(distance: {coord_check['distance_meters']:.1f}m)"
                )
                vr.message = "Coordinates do not match official records"

            vr.verified_at = datetime.utcnow()
            db.commit()
            return vr

        except Exception:
            logger.exception("Unexpected verification error")
            vr.status = "failed"
            vr.message = "Internal verification error"
            db.commit()
            return vr

    # ------------------------------------------------------------------

    def _search_registry(
        self,
        request: VerificationRequestCreate,
    ) -> Optional[LandRegistry]:
        """Search registry using exact match, then proximity match"""

        from sqlmodel import Session

        with Session(engine) as session:
            logger.debug("Searching registry (exact match)")

            stmt = select(LandRegistry).where(
                LandRegistry.town.ilike(f"%{request.town}%"),
                LandRegistry.layout.ilike(f"%{request.layout}%"),
                LandRegistry.block_number == request.block_number,
                LandRegistry.plot_number == request.plot_number,
                LandRegistry.is_active.is_(True),
            )

            result = session.exec(stmt).first()
            if result:
                logger.info(
                    "Exact registry match found | registry_id=%s",
                    result.id,
                )
                return result

            logger.debug("No exact match found, running proximity search")

            if not request.coordinates:
                logger.warning("No coordinates supplied for proximity search")
                return None

            stmt = (
                select(LandRegistry)
                .where(
                    LandRegistry.town.ilike(f"%{request.town}%"),
                    LandRegistry.is_active.is_(True),
                )
                .limit(20)
            )

            candidates = session.exec(stmt).all()

            submitted_points = geometry.points_to_list(
                [{"lat": c.lat, "lng": c.lng} for c in request.coordinates]
            )
            submitted_center = geometry.calculate_centroid(submitted_points)

            best_match = None
            min_distance = float("inf")

            for record in candidates:
                if not record.coordinates:
                    continue

                official_points = geometry.points_to_list(record.coordinates)
                official_center = geometry.calculate_centroid(official_points)

                distance = geometry.haversine_distance(
                    submitted_center,
                    official_center,
                )

                logger.debug(
                    "Proximity check | registry_id=%s | distance=%.2fm",
                    record.id,
                    distance,
                )

                if distance < min_distance and distance < 50:
                    min_distance = distance
                    best_match = record

            if best_match:
                logger.info(
                    "Proximity registry match found | registry_id=%s | distance=%.2fm",
                    best_match.id,
                    min_distance,
                )

            return best_match

    # ------------------------------------------------------------------

    def get_history(
        self,
        db: Session,
        user_id: int,
        limit: int = 50,
    ) -> list:
        """Get user's verification history"""

        stmt = (
            select(VerificationRequest)
            .where(VerificationRequest.user_id == user_id)
            .order_by(VerificationRequest.requested_at.desc())
            .limit(limit)
        )

        return db.exec(stmt).all()


# Global instance
verifier = SimpleVerifier()
