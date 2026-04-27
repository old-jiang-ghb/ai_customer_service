"""共享 fixture：供 tests/dao、tests/service 复用（从项目根目录执行 pytest 时加载）。"""

from __future__ import annotations

# 必须在导入本项目任何模块（尤其是 core.database）之前执行：
# SQLAlchemy URL 使用 mysql+mysqldb 时会 import MySQLdb；用 PyMySQL 注册同名模块避免
# ModuleNotFoundError: No module named 'MySQLdb'。
import pymysql

pymysql.install_as_MySQLdb()

from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session as SaSession


@pytest.fixture
def mock_sqlalchemy_session():
    """模拟 sqlalchemy.orm.Session；query 返回可链式调用的 Query mock。"""
    from types import SimpleNamespace

    db = MagicMock(spec=SaSession)
    query = MagicMock()
    db.query.return_value = query
    query.filter.return_value = query
    query.filter_by.return_value = query
    query.order_by.return_value = query
    query.offset.return_value = query
    query.limit.return_value = query

    return SimpleNamespace(db=db, query=query)
