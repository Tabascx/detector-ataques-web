from detector import analizar_linea


def test_detecta_sql_injection_union_select():
    linea = 'GET /product?id=1 UNION SELECT username,password FROM users HTTP/1.1'
    assert analizar_linea(linea) == "SQL Injection"


def test_detecta_sql_injection_or_1_1():
    linea = "GET /login?user=admin' OR 1=1-- HTTP/1.1"
    assert analizar_linea(linea) == "SQL Injection"


def test_detecta_xss_script_tag():
    linea = 'GET /search?q=<script>alert(1)</script> HTTP/1.1'
    assert analizar_linea(linea) == "XSS"


def test_detecta_xss_javascript_uri():
    linea = 'GET /redirect?url=javascript:alert(1) HTTP/1.1'
    assert analizar_linea(linea) == "XSS"


def test_detecta_path_traversal():
    linea = 'GET /files/../../etc/passwd HTTP/1.1'
    assert analizar_linea(linea) == "Path Traversal"


def test_detecta_command_injection():
    linea = 'POST /upload; cat /etc/shadow HTTP/1.1'
    assert analizar_linea(linea) == "Command Injection"


def test_no_detecta_falso_positivo_texto_normal():
    """Una peticion normal de navegacion no debe disparar ninguna alerta."""
    linea = 'GET /productos/zapatillas-running HTTP/1.1'
    assert analizar_linea(linea) is None


def test_no_detecta_falso_positivo_con_palabra_select_legitima():
    """La palabra 'select' sola (como en un <select> de formulario) no
    debe confundirse con SQL Injection, que requiere UNION SELECT."""
    linea = 'GET /formulario?campo=select-pais HTTP/1.1'
    assert analizar_linea(linea) is None


def test_no_detecta_falso_positivo_login_normal():
    linea = 'GET /login?user=maria&pass=hunter2 HTTP/1.1'
    assert analizar_linea(linea) is None


def test_deteccion_no_distingue_mayusculas():
    """Los atacantes a veces varian mayusculas/minusculas para evadir
    filtros basicos; el detector debe seguir detectandolo."""
    linea = "GET /login?user=admin' Or 1=1-- HTTP/1.1"
    assert analizar_linea(linea) == "SQL Injection"
