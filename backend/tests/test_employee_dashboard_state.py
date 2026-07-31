from datetime import UTC, datetime

from backend.database.enums import ChannelStatus, ChannelType, DialogStatus
from backend.database.models.channel import Channel
from backend.database.models.dialog import Dialog
from backend.database.models.employee import Employee


def make_employee() -> Employee:
    return Employee(
        owner_id=1,
        name="Анна",
        role="Поддержка",
        instruction="Помогай клиентам",
        fallback_message="Передам вопрос оператору",
        status="active",
    )


def test_employee_exposes_persisted_channel_state() -> None:
    employee = make_employee()
    connected_at = datetime.now(UTC)
    employee.channels = [
        Channel(
            employee_id=1,
            type=ChannelType.TELEGRAM,
            status=ChannelStatus.CONNECTED,
            external_username="sentra_bot",
            connected_at=connected_at,
        ),
        Channel(
            employee_id=1,
            type=ChannelType.MAX,
            status=ChannelStatus.DISCONNECTED,
        ),
    ]

    assert employee.telegram_connected is True
    assert employee.telegram_bot_username == "sentra_bot"
    assert employee.telegram_connected_at == connected_at
    assert employee.max_connected is False


def test_employee_counts_open_and_human_pending_dialogs() -> None:
    employee = make_employee()
    employee.dialogs = [
        Dialog(
            employee_id=1,
            client_external_id="active",
            status=DialogStatus.ACTIVE,
        ),
        Dialog(
            employee_id=1,
            client_external_id="pending",
            status=DialogStatus.NEEDS_HUMAN,
        ),
        Dialog(
            employee_id=1,
            client_external_id="resolved",
            status=DialogStatus.RESOLVED,
        ),
    ]

    assert employee.dialogs_count == 3
    assert employee.active_dialogs_count == 2
    assert employee.human_pending_count == 1
