"""
SessionHistoryService 单元测试：mock SQLAlchemy Session + patch 业务依赖。

权限校验：session_id 必须出现在当前 user_id 的会话列表中，否则抛出 BusinessException。

patch 目标使用「调用方模块内的名字」，避免 ImportError::
    service.session_history_service.SessionDao
    service.session_history_service.SessionHistoryDao

运行方式（在 ai_customer_service 根目录）::
    pytest tests/service/test_session_history_service.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.exception import BusinessException
from service.session_history_service import SessionHistoryService


def _make_session_row(session_id: int, user_id: int = 1):
    """构造带 .id 的伪 ORM 对象，模拟 models.session.Session。"""
    m = MagicMock()
    m.id = session_id
    m.user_id = user_id
    return m


@pytest.fixture
def mock_db(mock_sqlalchemy_session):
    """SQLAlchemy Session mock（不连库）。"""
    return mock_sqlalchemy_session.db


# ---------------------------------------------------------------------------
# 权限：session_id 必须属于当前 user_id
# ---------------------------------------------------------------------------


@patch("service.session_history_service.SessionHistoryDao.get_by_session_id")
@patch("service.session_history_service.SessionDao.get_session_by_user_id")
def test_get_by_session_id_allowed_returns_histories(
    mock_get_sessions, mock_get_histories, mock_db
):
    """正常：session_id 属于当前用户时，返回 SessionHistoryDao 查询结果。"""
    mock_get_sessions.return_value = [
        _make_session_row(1),
        _make_session_row(42),
    ]
    expected = [MagicMock(), MagicMock()]
    mock_get_histories.return_value = expected

    result = SessionHistoryService.get_by_session_id(mock_db, session_id=42, user_id=100)

    assert result is expected
    mock_get_sessions.assert_called_once_with(mock_db, 100)
    mock_get_histories.assert_called_once_with(mock_db, 42)


@patch("service.session_history_service.SessionHistoryDao.get_by_session_id")
@patch("service.session_history_service.SessionDao.get_session_by_user_id")
def test_get_by_session_id_denied_raises_business_exception(
    mock_get_sessions, mock_get_histories, mock_db
):
    """权限拒绝：请求的 session_id 不在该用户会话列表中，不调用历史 DAO。"""
    mock_get_sessions.return_value = [_make_session_row(1), _make_session_row(2)]

    with pytest.raises(BusinessException) as exc_info:
        SessionHistoryService.get_by_session_id(mock_db, session_id=99, user_id=1)

    assert "当前会话不属于当前登录用户" in exc_info.value.msg
    mock_get_histories.assert_not_called()


@patch("service.session_history_service.SessionHistoryDao.get_by_session_id")
@patch("service.session_history_service.SessionDao.get_session_by_user_id")
def test_get_by_session_id_denied_empty_sessions(
    mock_get_sessions, mock_get_histories, mock_db
):
    """边界：用户没有任何会话时，任意 session_id 均被拒绝。"""
    mock_get_sessions.return_value = []

    with pytest.raises(BusinessException):
        SessionHistoryService.get_by_session_id(mock_db, session_id=1, user_id=1)

    mock_get_histories.assert_not_called()


@patch("service.session_history_service.SessionHistoryDao.get_by_session_id")
@patch("service.session_history_service.SessionDao.get_session_by_user_id")
def test_get_by_session_id_id_match_strict_equality(
    mock_get_sessions, mock_get_histories, mock_db
):
    """边界：session_id 与列表中 id 必须相等（类型一致时才算匹配）。"""
    mock_get_sessions.return_value = [_make_session_row(10)]
    mock_get_histories.return_value = []

    SessionHistoryService.get_by_session_id(mock_db, session_id=10, user_id=1)
    mock_get_histories.assert_called_once_with(mock_db, 10)


# ---------------------------------------------------------------------------
# 异常：DAO 层失败向上抛出（不吞异常）
# ---------------------------------------------------------------------------


@patch("service.session_history_service.SessionDao.get_session_by_user_id")
def test_get_by_session_id_list_sessions_raises(mock_get_sessions, mock_db):
    """异常：拉取用户会话列表失败。"""
    mock_get_sessions.side_effect = RuntimeError("db down")

    with pytest.raises(RuntimeError, match="db down"):
        SessionHistoryService.get_by_session_id(mock_db, session_id=1, user_id=1)


@patch("service.session_history_service.SessionHistoryDao.get_by_session_id")
@patch("service.session_history_service.SessionDao.get_session_by_user_id")
def test_get_by_session_id_history_dao_raises_after_permission_ok(
    mock_get_sessions, mock_get_histories, mock_db
):
    """异常：权限通过后，拉取历史记录失败。"""
    mock_get_sessions.return_value = [_make_session_row(5)]
    mock_get_histories.side_effect = RuntimeError("history query failed")

    with pytest.raises(RuntimeError, match="history query failed"):
        SessionHistoryService.get_by_session_id(mock_db, session_id=5, user_id=1)


# ---------------------------------------------------------------------------
# 返回值边界
# ---------------------------------------------------------------------------


@patch("service.session_history_service.SessionHistoryDao.get_by_session_id")
@patch("service.session_history_service.SessionDao.get_session_by_user_id")
def test_get_by_session_id_returns_empty_list_when_no_history(
    mock_get_sessions, mock_get_histories, mock_db
):
    """边界：有权访问但无历史记录时返回空列表。"""
    mock_get_sessions.return_value = [_make_session_row(7)]
    mock_get_histories.return_value = []

    assert SessionHistoryService.get_by_session_id(mock_db, session_id=7, user_id=2) == []
