"""
SessionDao 单元测试：仅用 mock 模拟 SQLAlchemy Session，不连接数据库。

运行方式（在 ai_customer_service 根目录）::
    pytest tests/dao/test_session_dao.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, call

import pytest
from sqlalchemy.exc import SQLAlchemyError

# 保证从任意 cwd 执行时仍能导入 dao / models（tests/dao → 项目根为 parents[2]）
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dao.session_dao import SessionDao
from models.session import Session as SessionModel


@pytest.fixture
def mock_db_session(mock_sqlalchemy_session):
    """与 conftest 中 mock_sqlalchemy_session 对齐的别名，便于本文件阅读。"""
    return mock_sqlalchemy_session


# --- get_session ---


def test_get_session_found(mock_db_session):
    row = MagicMock(spec=SessionModel)
    mock_db_session.query.first.return_value = row

    assert SessionDao.get_session(mock_db_session.db, 10) is row
    mock_db_session.db.query.assert_called_once_with(SessionModel)
    assert mock_db_session.query.filter.call_count == 2


def test_get_session_not_found(mock_db_session):
    mock_db_session.query.first.return_value = None
    assert SessionDao.get_session(mock_db_session.db, 999) is None


def test_get_session_id_zero_boundary(mock_db_session):
    mock_db_session.query.first.return_value = None
    SessionDao.get_session(mock_db_session.db, 0)
    mock_db_session.db.query.assert_called_once_with(SessionModel)


def test_get_session_query_raises(mock_db_session):
    mock_db_session.db.query.side_effect = SQLAlchemyError("query failed")
    with pytest.raises(SQLAlchemyError):
        SessionDao.get_session(mock_db_session.db, 1)


def test_get_session_first_raises(mock_db_session):
    mock_db_session.query.first.side_effect = SQLAlchemyError("timeout")
    with pytest.raises(SQLAlchemyError):
        SessionDao.get_session(mock_db_session.db, 1)


# --- create_session ---


def test_create_session_success(mock_db_session):
    session_obj = MagicMock(spec=SessionModel)
    out = SessionDao.create_session(mock_db_session.db, session_obj)
    assert out is session_obj
    assert mock_db_session.db.mock_calls[-3:] == [
        call.add(session_obj),
        call.flush(),
        call.refresh(session_obj),
    ]


def test_create_session_flush_raises(mock_db_session):
    session_obj = MagicMock(spec=SessionModel)
    mock_db_session.db.flush.side_effect = SQLAlchemyError("flush failed")
    with pytest.raises(SQLAlchemyError):
        SessionDao.create_session(mock_db_session.db, session_obj)
    mock_db_session.db.refresh.assert_not_called()


def test_create_session_refresh_raises(mock_db_session):
    session_obj = MagicMock(spec=SessionModel)
    mock_db_session.db.refresh.side_effect = SQLAlchemyError("refresh failed")
    with pytest.raises(SQLAlchemyError):
        SessionDao.create_session(mock_db_session.db, session_obj)


# --- get_session_by_user_id ---


def test_get_session_by_user_id_returns_rows(mock_db_session):
    rows = [MagicMock(spec=SessionModel)]
    mock_db_session.query.all.return_value = rows
    assert SessionDao.get_session_by_user_id(mock_db_session.db, 1) == rows


def test_get_session_by_user_id_empty(mock_db_session):
    mock_db_session.query.all.return_value = []
    assert SessionDao.get_session_by_user_id(mock_db_session.db, 1) == []


def test_get_session_by_user_id_all_raises(mock_db_session):
    mock_db_session.query.all.side_effect = SQLAlchemyError("read error")
    with pytest.raises(SQLAlchemyError):
        SessionDao.get_session_by_user_id(mock_db_session.db, 1)


# --- get_session_paging ---


def test_get_session_paging_first_page(mock_db_session):
    mock_db_session.query.all.return_value = []
    SessionDao.get_session_paging(mock_db_session.db, pno=1, page_size=10)
    mock_db_session.query.offset.assert_called_once_with(0)
    mock_db_session.query.limit.assert_called_once_with(10)


def test_get_session_paging_second_page_offset(mock_db_session):
    mock_db_session.query.all.return_value = []
    SessionDao.get_session_paging(mock_db_session.db, pno=2, page_size=10)
    mock_db_session.query.offset.assert_called_once_with(10)


def test_get_session_paging_with_user_id_extra_filter(mock_db_session):
    mock_db_session.query.all.return_value = []
    SessionDao.get_session_paging(mock_db_session.db, 1, 10, user_id=7)
    assert mock_db_session.query.filter.call_count == 2


def test_get_session_paging_user_id_none_single_filter(mock_db_session):
    mock_db_session.query.all.return_value = []
    SessionDao.get_session_paging(mock_db_session.db, 1, 10, user_id=None)
    assert mock_db_session.query.filter.call_count == 1


def test_get_session_paging_page_size_zero(mock_db_session):
    mock_db_session.query.all.return_value = []
    SessionDao.get_session_paging(mock_db_session.db, 1, page_size=0)
    mock_db_session.query.limit.assert_called_once_with(0)


def test_get_session_paging_order_by_raises(mock_db_session):
    mock_db_session.query.order_by.side_effect = SQLAlchemyError("order failed")
    with pytest.raises(SQLAlchemyError):
        SessionDao.get_session_paging(mock_db_session.db, 1, 10)


# --- get_session_count ---


def test_get_session_count_all(mock_db_session):
    mock_db_session.query.count.return_value = 100
    assert SessionDao.get_session_count(mock_db_session.db) == 100


def test_get_session_count_with_user(mock_db_session):
    mock_db_session.query.count.return_value = 3
    assert SessionDao.get_session_count(mock_db_session.db, user_id=99) == 3
    assert mock_db_session.query.filter.call_count == 2


def test_get_session_count_raises(mock_db_session):
    mock_db_session.query.count.side_effect = SQLAlchemyError("count failed")
    with pytest.raises(SQLAlchemyError):
        SessionDao.get_session_count(mock_db_session.db)
