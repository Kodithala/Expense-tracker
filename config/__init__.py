# Init file for config package
try:
    import pymysql
    pymysql.install_as_MySQLdb()

    from django.db.backends.base.base import BaseDatabaseWrapper
    BaseDatabaseWrapper.check_database_version_supported = lambda self: None
except Exception:
    pass


