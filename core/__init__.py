from pathlib import Path

from dynaconf import Dynaconf

# 项目路径
__BASE_DIR = Path(__file__).parent.parent

settings_files = [
    # 测试环境
    Path(__file__).parent / "dev.yml",
    # 生产环境
    # Path(__file__).parent / "prod.yml",
]

settings = Dynaconf(
    settings_files=settings_files,
    lowercase_read = False,     # 禁止配置小写
    base_dir = __BASE_DIR,     # 项目目录
    envvar_prefix="EMP_CONF"  # 环境变量前缀。
)