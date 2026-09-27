from app.db import connect

def list_fabrics():
    c = connect()
    try:
        return [dict(r) for r in c.execute("SELECT * FROM fabrics ORDER BY id").fetchall()]
    finally:
        c.close()

def get_fabric(fid: int):
    c = connect()
    try:
        r = c.execute("SELECT * FROM fabrics WHERE id=?", (fid,)).fetchone()
        return dict(r) if r else None
    finally:
        c.close()

def update_hems(fid: int, hem_top: float, hem_bottom: float):
    c = connect()
    try:
        c.execute(
            "UPDATE fabrics SET hem_top=?, hem_bottom=? WHERE id=?",
            (hem_top, hem_bottom, fid),
        )
        c.commit()
        r = c.execute("SELECT * FROM fabrics WHERE id=?", (fid,)).fetchone()
        return dict(r) if r else None
    finally:
        c.close()
