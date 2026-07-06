from ddg_router.server import normalize_model, serve, _FREE_GET


def test_normalize_strips_ddg_prefix():
    assert normalize_model("ddg/glm-4.5-air") == "glm-4.5-air"


def test_normalize_auto_maps_to_default():
    assert normalize_model("ddg/auto", default="nano") == "nano"
    assert normalize_model("auto", default="nano") == "nano"
    assert normalize_model("", default="nano") == "nano"


def test_normalize_plain_passthrough():
    assert normalize_model("glm-4.5-air") == "glm-4.5-air"


def test_normalize_nonstring_passthrough():
    assert normalize_model(None) is None


def test_free_get_routes_and_serve():
    assert "/v1/models" in _FREE_GET
    assert callable(serve)
