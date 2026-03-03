import httpx
import logging
from app.config import get_settings
from app.models.models import User

logger = logging.getLogger(__name__)
settings = get_settings()


async def create_bitrix_lead(user: User) -> dict:
    if not settings.BITRIX24_URL or not settings.BITRIX24_WEBHOOK:
        logger.warning("Bitrix24 not configured, skipping lead creation")
        return {"error": "Bitrix24 not configured"}

    lead_data = {
        "TITLE": f"TG-Лид: {user.full_name or 'Без имени'}",
        "NAME": user.full_name or "Без имени",
        "PHONE": [{"VALUE": user.phone, "VALUE_TYPE": "WORK"}] if user.phone else [],
        "SOURCE_ID": "WEB",
        "UTM_SOURCE": user.utm_source,
        "UTM_MEDIUM": user.utm_medium,
        "UTM_CAMPAIGN": user.utm_campaign,
        "COMMENTS": (
            f"Telegram ID: {user.telegram_id}\n"
            f"Username: @{user.username}\n"
            f"Источник: {user.source}\n"
            f"Форма: {user.form_name}"
        )
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            webhook_url = settings.BITRIX24_URL.rstrip('/') + '/' + settings.BITRIX24_WEBHOOK.lstrip('/')
            response = await client.post(
                f"{webhook_url}/crm.lead.add.json",
                json={"fields": lead_data},
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Successfully created Bitrix24 lead for user {user.id}")
            return result
    except httpx.HTTPStatusError as e:
        logger.error(f"Bitrix24 API error: {e.response.text}")
        return {"error": f"API error: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"Failed to create Bitrix24 lead: {e}")
        return {"error": str(e)}
