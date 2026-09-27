import os
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="curtainlen_test_")

from fastapi.testclient import TestClient
from app.main import app

# 种子数据: 窗1 客厅落地窗 3.0x2.6 褶倍2.0; 布1 遮光1.4m 门幅1.4 上折边0.10 下折边0.15
WINDOW_ID = 1
FABRIC_ID = 1


def _client():
    return TestClient(app)


def _set_hems(client, hem_top, hem_bottom):
    r = client.put(f"/api/fabrics/{FABRIC_ID}/hems", json={"hem_top": hem_top, "hem_bottom": hem_bottom})
    assert r.status_code == 200
    return r.json()


def test_update_hems_persists():
    with _client() as c:
        body = _set_hems(c, 0.20, 0.30)
        assert body["hem_top"] == 0.20
        assert body["hem_bottom"] == 0.30
        got = c.get(f"/api/fabrics/{FABRIC_ID}").json()
        assert got["hem_top"] == 0.20
        assert got["hem_bottom"] == 0.30


def test_negative_hem_rejected_and_not_overwritten():
    with _client() as c:
        _set_hems(c, 0.10, 0.15)
        r = c.put(f"/api/fabrics/{FABRIC_ID}/hems", json={"hem_top": -0.5, "hem_bottom": 0.15})
        assert r.status_code == 422
        r = c.put(f"/api/fabrics/{FABRIC_ID}/hems", json={"hem_top": 0.10, "hem_bottom": -0.01})
        assert r.status_code == 422
        got = c.get(f"/api/fabrics/{FABRIC_ID}").json()
        assert got["hem_top"] == 0.10
        assert got["hem_bottom"] == 0.15


def test_estimate_uses_updated_hems():
    with _client() as c:
        _set_hems(c, 0.20, 0.30)
        r = c.get(f"/api/estimate?window_id={WINDOW_ID}&fabric_id={FABRIC_ID}")
        assert r.status_code == 200
        est = r.json()
        # cut_height = 2.6 + 0.20 + 0.30; panels = ceil(3.0*2.0/1.4) = 5
        assert est["cut_height"] == 3.1
        assert est["panels"] == 5
        assert est["meters"] == round(5 * 3.1, 2)
        # 算料结果回包的折边与布料详情一致
        assert est["fabric"]["hem_top"] == 0.20
        assert est["fabric"]["hem_bottom"] == 0.30


def test_history_keeps_cut_height_as_written():
    with _client() as c:
        _set_hems(c, 0.10, 0.15)
        old = c.post("/api/estimate", json={"window_id": WINDOW_ID, "fabric_id": FABRIC_ID, "save": True}).json()
        assert old["cut_height"] == 2.85
        _set_hems(c, 0.50, 0.60)
        new = c.post("/api/estimate", json={"window_id": WINDOW_ID, "fabric_id": FABRIC_ID, "save": True}).json()
        assert new["cut_height"] == 3.7
        runs = {r["id"]: r for r in c.get("/api/runs").json()["items"]}
        assert runs[old["run_id"]]["result"]["cut_height"] == 2.85
        assert runs[new["run_id"]]["result"]["cut_height"] == 3.7
