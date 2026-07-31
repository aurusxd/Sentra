import unittest
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

max_webhook_router = import_module("backend.api.routers.max_webhook_router")


class MaxOperatorCallbackTests(unittest.IsolatedAsyncioTestCase):
    def test_extracts_identity_from_current_max_callback_shape(self) -> None:
        update = {
            "update_type": "message_callback",
            "message": {
                "sender": {"user_id": 7001},
                "recipient": {"chat_id": 9001},
            },
            "callback": {
                "callback_id": "callback-1",
                "payload": "signed-payload",
                "user": {"user_id": 7001},
            },
        }

        self.assertEqual(
            max_webhook_router.get_callback_admin_identity(update),
            (9001, 7001),
        )

    def test_falls_back_to_message_sender_when_callback_user_is_absent(self) -> None:
        update = {
            "update_type": "message_callback",
            "message": {
                "sender": {"user_id": 7002},
                "recipient": {"chat_id": 9002},
            },
            "callback": {
                "callback_id": "callback-2",
                "payload": "signed-payload",
            },
        }

        self.assertEqual(
            max_webhook_router.get_callback_admin_identity(update),
            (9002, 7002),
        )

    async def test_take_callback_starts_operator_session(self) -> None:
        update = {
            "update_type": "message_callback",
            "message": {
                "sender": {"user_id": 7003},
                "recipient": {"chat_id": 9003},
            },
            "callback": {
                "callback_id": "callback-3",
                "payload": "signed-payload",
                "user": {"user_id": 7003},
            },
        }
        channel = SimpleNamespace(id=31)
        employee = SimpleNamespace(id=41, max_admin_chat_id="9003")
        dialog = SimpleNamespace(
            id=51,
            channel_id=31,
            employee_id=41,
            client_name="Иван",
        )

        get_by_id = AsyncMock(return_value=dialog)
        start_session = AsyncMock(return_value=dialog)
        answer_callback = AsyncMock(return_value=True)
        send_status = AsyncMock()

        with (
            patch.object(
                max_webhook_router,
                "parse_max_operator_callback",
                return_value=("take", 51),
            ),
            patch.object(max_webhook_router.dialog_service, "get_by_id", get_by_id),
            patch.object(
                max_webhook_router.dialog_service,
                "start_max_operator_session",
                start_session,
            ),
            patch.object(
                max_webhook_router.max_service,
                "answer_callback",
                answer_callback,
            ),
            patch.object(max_webhook_router, "send_operator_status", send_status),
        ):
            result = await max_webhook_router.handle_operator_callback(
                update=update,
                channel=channel,
                employee=employee,
                token="token",
            )

        self.assertEqual(result, {"success": True})
        start_session.assert_awaited_once_with(
            dialog_id=51,
            channel_id=31,
            admin_chat_id="9003",
            admin_user_id="7003",
        )
        answer_callback.assert_awaited_once_with(
            "token",
            "callback-3",
            "Диалог принят",
        )
        send_status.assert_awaited_once()

    async def test_callback_uses_configured_chat_for_original_notification(self) -> None:
        update = {
            "update_type": "message_callback",
            "message": {
                "body": {"mid": "notification-55"},
            },
            "callback": {
                "callback_id": "callback-55",
                "payload": "signed-payload",
                "user": {"user_id": 7055},
            },
        }
        channel = SimpleNamespace(id=31)
        employee = SimpleNamespace(id=41, max_admin_chat_id="9003")
        dialog = SimpleNamespace(
            id=55,
            channel_id=31,
            employee_id=41,
            client_name="Пётр",
            max_admin_notification_message_id="notification-55",
        )
        start_session = AsyncMock(return_value=dialog)

        with (
            patch.object(
                max_webhook_router,
                "parse_max_operator_callback",
                return_value=("take", 55),
            ),
            patch.object(
                max_webhook_router.dialog_service,
                "get_by_id",
                AsyncMock(return_value=dialog),
            ),
            patch.object(
                max_webhook_router.dialog_service,
                "start_max_operator_session",
                start_session,
            ),
            patch.object(
                max_webhook_router.max_service,
                "answer_callback",
                AsyncMock(return_value=True),
            ),
            patch.object(
                max_webhook_router,
                "send_operator_status",
                AsyncMock(),
            ),
        ):
            result = await max_webhook_router.handle_operator_callback(
                update=update,
                channel=channel,
                employee=employee,
                token="token",
            )

        self.assertEqual(result, {"success": True})
        start_session.assert_awaited_once_with(
            dialog_id=55,
            channel_id=31,
            admin_chat_id="9003",
            admin_user_id="7055",
        )

    async def test_first_admin_message_auto_takes_single_pending_dialog(self) -> None:
        pending_dialog = SimpleNamespace(id=54, client_name="Анна")
        active_dialog = SimpleNamespace(
            id=54,
            client_name="Анна",
            client_external_id="client-chat-54",
            max_operator_user_id="7006",
        )
        start_session = AsyncMock(return_value=active_dialog)
        send_status = AsyncMock()
        send_message = AsyncMock(return_value={"body": {"mid": "client-message-54"}})

        with (
            patch.object(
                max_webhook_router.dialog_service,
                "get_active_max_operator_dialog",
                AsyncMock(return_value=None),
            ),
            patch.object(
                max_webhook_router.dialog_service,
                "get_single_pending_max_operator_dialog",
                AsyncMock(return_value=pending_dialog),
            ),
            patch.object(
                max_webhook_router.dialog_service,
                "start_max_operator_session",
                start_session,
            ),
            patch.object(max_webhook_router, "send_operator_status", send_status),
            patch.object(
                max_webhook_router.message_service,
                "human_message_exists",
                AsyncMock(return_value=False),
            ),
            patch.object(max_webhook_router.max_service, "send_message", send_message),
            patch.object(
                max_webhook_router.message_service,
                "create_human_message",
                AsyncMock(),
            ),
        ):
            result = await max_webhook_router.handle_admin_message(
                message={"body": {"mid": "admin-message-54", "text": "Добрый день"}},
                channel=SimpleNamespace(id=31),
                token="token",
                admin_chat_id="9003",
                sender_id=7006,
                text="Добрый день",
            )

        self.assertEqual(result, {"success": True})
        start_session.assert_awaited_once_with(
            dialog_id=54,
            channel_id=31,
            admin_chat_id="9003",
            admin_user_id="7006",
        )
        send_message.assert_awaited_once_with(
            token="token",
            chat_id="client-chat-54",
            text="Добрый день",
        )
        send_status.assert_awaited_once()

    async def test_operator_message_is_forwarded_after_takeover(self) -> None:
        dialog = SimpleNamespace(
            id=52,
            client_external_id="client-chat",
            max_operator_user_id="7004",
        )
        get_active_dialog = AsyncMock(return_value=dialog)
        human_message_exists = AsyncMock(return_value=False)
        send_message = AsyncMock(return_value={"body": {"mid": "client-message"}})
        create_human_message = AsyncMock()

        with (
            patch.object(
                max_webhook_router.dialog_service,
                "get_active_max_operator_dialog",
                get_active_dialog,
            ),
            patch.object(
                max_webhook_router.message_service,
                "human_message_exists",
                human_message_exists,
            ),
            patch.object(
                max_webhook_router.max_service,
                "send_message",
                send_message,
            ),
            patch.object(
                max_webhook_router.message_service,
                "create_human_message",
                create_human_message,
            ),
        ):
            result = await max_webhook_router.handle_admin_message(
                message={"body": {"mid": "admin-message", "text": "Здравствуйте"}},
                channel=SimpleNamespace(id=31),
                token="token",
                admin_chat_id="9003",
                sender_id=7004,
                text="Здравствуйте",
            )

        self.assertEqual(result, {"success": True})
        send_message.assert_awaited_once_with(
            token="token",
            chat_id="client-chat",
            text="Здравствуйте",
        )
        create_human_message.assert_awaited_once_with(
            dialog_id=52,
            text="Здравствуйте",
            external_message_id="admin-message",
        )

    async def test_done_command_stops_active_operator_session(self) -> None:
        dialog = SimpleNamespace(id=53, max_operator_user_id="7005")
        get_active_dialog = AsyncMock(return_value=dialog)
        stop_session = AsyncMock(return_value=dialog)
        send_status = AsyncMock()

        with (
            patch.object(
                max_webhook_router.dialog_service,
                "get_active_max_operator_dialog",
                get_active_dialog,
            ),
            patch.object(
                max_webhook_router.dialog_service,
                "stop_max_operator_session",
                stop_session,
            ),
            patch.object(max_webhook_router, "send_operator_status", send_status),
        ):
            result = await max_webhook_router.handle_admin_message(
                message={"body": {"mid": "done-message", "text": "/готово"}},
                channel=SimpleNamespace(id=31),
                token="token",
                admin_chat_id="9003",
                sender_id=7005,
                text="/готово",
            )

        self.assertEqual(result, {"success": True})
        stop_session.assert_awaited_once_with(53, resolved=True)
        send_status.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
