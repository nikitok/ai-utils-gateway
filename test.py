# apps/core/src/routers/superadmin_downgrade.py
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from uuid import UUID
import logging
import base64
from src.models import User, UserRole
from src.schemas.users import SuperAdminPromotionRequest
from src.config.database import get_db
from src.config.dependencies.auth_user import get_current_user_sdk
from src.config.settings import settings
from auth_sdk.dependencies import AuthContext

logger = logging.getLogger(__name__)

# Create a dedicated router with a different prefix to avoid conflicts
router = APIRouter(prefix="/superadmin", tags=["superadmin-operations"])


# -----------------------------------------------------------------------------
# 🔒 POST: Downgrade Superadmin to User (Hidden Endpoint - Superadmin Only)
# -----------------------------------------------------------------------------
@router.post("/downgrade", include_in_schema=False, response_model=Dict[str, Any])
def downgrade_superadmin_to_user(
        downgrade_request: SuperAdminPromotionRequest = Body(...),
        current_user: AuthContext = Depends(get_current_user_sdk(required_roles=["superadmin"])),
        db: Session = Depends(get_db)
):
    """
    Hidden endpoint to downgrade a superadmin to user role.
    - Requires superadmin privileges to access
    - Requires the correct secret code from environment
    - Requires the exact DOWNGRADE2user confirmation string
    - Base64 encoded secret code with 24 characters minimum length (in env)
    - Prevents self-downgrading
    - Ensures at least one superadmin remains in the system
    """
    admin_user = current_user.user
    # Verify the confirmation string is exactly as required (case sensitive)
    if downgrade_request.DOWNGRADE2user != "DOWNGRADE2user":
        logger.warning(f"❌ Invalid confirmation string attempt by {admin_user.email}")
        raise HTTPException(status_code=403, detail="📖 Wrong spellbook. Try 'Dark Arts 101' before casting irreversible actions")

    # Verify the secret code matches the one in settings
    if downgrade_request.SUPERADMIN_SECRET_CODE != settings.superadmin.SUPERADMIN_SECRET_CODE:
        # Use a generic error message to avoid exposing information
        logger.warning(f"❌ Invalid secret code attempt by {admin_user.email}")
        raise HTTPException(status_code=403, detail="💀 This action demands a sacrifice. In order to make it, you must lose that which you love.")

    # Verify the secret code is base64 encoded and at least 24 chars
    try:
        decoded = base64.b64decode(settings.superadmin.SUPERADMIN_SECRET_CODE)
        if len(settings.superadmin.SUPERADMIN_SECRET_CODE) < 24:
            logger.error("❌ SUPERADMIN_SECRET_CODE is too short, should be at least 24 characters")
            raise HTTPException(status_code=500, detail="Server configuration error")
    except Exception:
        logger.error("❌ SUPERADMIN_SECRET_CODE is not valid base64")
        raise HTTPException(status_code=500, detail="Server configuration error")

    # Find the user to downgrade
    user = db.query(User).filter(User.id == downgrade_request.user_id).first()
    if not user:
        logger.warning(f"🚫 User with ID {downgrade_request.user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

    # Check that the user is not trying to downgrade themselves
    if user.id == admin_user.id:
        logger.warning(f"⚠️ User {admin_user.email} attempted to downgrade themselves")
        raise HTTPException(status_code=403, detail="🫠 You're not allowed to fade into irrelevance on your own terms.")

    # Check that the user is actually a superadmin
    if user.role != UserRole.SUPERADMIN:
        logger.warning(f"⚠️ Attempted to downgrade non-superadmin user {user.email}")
        raise HTTPException(status_code=400, detail="🕳️ You can't demote someone who's already insignificant. Try promoting them first—it'll be more satisfying.")

    # Ensure at least one superadmin remains in the system
    superadmins = db.query(User).filter(User.role == UserRole.SUPERADMIN).with_for_update().all()
    if len(superadmins) <= 1:
        raise HTTPException(status_code=403, detail="🩸 The Throne cannot be empty. One must always rule.")

    # Downgrade user to regular user role
    user.role = UserRole.USER
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Database error while downgrading user {user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred while processing the request")

    logger.info(f"🔑 User {user.email} downgraded from superadmin to user by {admin_user.email}")

    return {"success": True, "message": f"🪓 Execution successful. {user.email} no longer holds the sacred key. Enjoy the silence."}




    # 2️⃣ 🚷 2️⃣ Step 4: B now attempts to downgrade A — but the database still considers B a regular user.
    # This means the "Throne must not be empty" guard should trigger.
    with patch('src.routers.superadmin_operations.settings.superadmin.SUPERADMIN_SECRET_CODE', test_secret_code), \
            patch('sqlalchemy.orm.Query.all', mock_superadmin_query): # 🟧 🟧 🟧 🟧 here's got the core hack 🟧 🟧 🟧 🟧