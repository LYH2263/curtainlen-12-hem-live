from fastapi.testclient import TestClient
from app.main import app
from app.repositories import fabrics as frepo, history as hrepo
from app.services import estimate_service

client = TestClient(app)


def _ids_by_name():
    return {f["name"]: f["id"] for f in frepo.list_fabrics()}


def test_hem_update_takes_effect_on_new_estimate():
    with TestClient(app) as c:
        fid = _ids_by_name()["遮光1.4m"]  # 门幅1.4 默认折边 0.10/0.15
        before = estimate_service.run_estimate(1, fid, False, "")
        assert before["cut_height"] == 2.85  # 2.6 + 0.10 + 0.15

        r = c.patch(f"/api/fabrics/{fid}/hems", json={"hem_top": 0.20, "hem_bottom": 0.30})
        assert r.status_code == 200
        assert r.json()["hem_top"] == 0.20 and r.json()["hem_bottom"] == 0.30

        after = estimate_service.run_estimate(1, fid, False, "")
        # 新折边当场进入 cut_height 与 meters
        assert after["cut_height"] == 3.10  # 2.6 + 0.20 + 0.30
        assert after["meters"] == round(after["panels"] * 3.10, 2)


def test_negative_hem_rejected_and_keeps_old_value():
    with TestClient(app) as c:
        fid = _ids_by_name()["纱帘2.8m"]
        orig = frepo.get_fabric(fid)
        r = c.patch(f"/api/fabrics/{fid}/hems", json={"hem_top": -0.01, "hem_bottom": 0.12})
        assert r.status_code == 422
        kept = frepo.get_fabric(fid)
        assert kept["hem_top"] == orig["hem_top"]
        assert kept["hem_bottom"] == orig["hem_bottom"]


def test_fabric_detail_hem_matches_estimate_payload():
    with TestClient(app):
        fid = _ids_by_name()["遮光1.4m"]
        frepo.update_hems(fid, 0.18, 0.22)
        detail = frepo.get_fabric(fid)
        out = estimate_service.run_estimate(1, fid, False, "")
        assert out["fabric"]["hem_top"] == detail["hem_top"] == 0.18
        assert out["fabric"]["hem_bottom"] == detail["hem_bottom"] == 0.22


def test_history_keeps_cut_height_snapshot():
    with TestClient(app):
        fid = _ids_by_name()["遮光1.4m"]
        frepo.update_hems(fid, 0.10, 0.15)
        saved = estimate_service.run_estimate(1, fid, True, "snap")
        run_id = saved["run_id"]
        old_cut = saved["cut_height"]
        # 之后再改折边，旧编号快照不变
        frepo.update_hems(fid, 0.5, 0.5)
        runs = hrepo.list_runs()
        row = next(r for r in runs if r["id"] == run_id)
        assert row["result"]["cut_height"] == old_cut
