def get_pg_connection_uri(conn):
    """
    Создает валидный URI из параметров хука.

    Args:
        conn: Соединение, полученное из хука.

    Returns:
        str: Строка URI для подключения к СУБД.
    """
    login = conn.login
    password = conn.password
    host = conn.host
    port = conn.port
    db = conn.schema
    extras_list = [f"{k}={v}" for k, v in conn.extra_dejson.items()]
    extras = f"&{'&'.join(extras_list)}" if extras_list else ''
    return f"jdbc:postgresql://{host}:{port}/{db}?user={login}&password={password}{extras}"

def get_mongo_connection_uri(conn):
    """
    Создает валидный URI из параметров хука.

    Args:
        conn: Соединение, полученное из хука.

    Returns:
        str: Строка URI для подключения к mongoDB.
    """
    login = conn.login
    password = conn.password
    host = conn.host
    port = conn.port
    db = conn.schema
    extras_list = [f"{k}={v}" for k, v in conn.extra_dejson.items()]
    extras = f"?{'&'.join(extras_list)}" if extras_list else ''
    return f"mongodb://{login}:{password}@{host}:{port}/{db}{extras}"