"""Descarga ICL e IPC de fuentes oficiales y guarda una copia en data/.

Lo ejecuta GitHub Actions todos los días. Si una fuente falla se prueba la
siguiente; si fallan todas, se conserva el archivo anterior sin tocarlo.
Solo usa la biblioteca estándar de Python.
"""
import json
import pathlib
import sys
import time
import urllib.request
from datetime import date, datetime, timezone

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
BCRA = "https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/"
UA = {"User-Agent": "calculadora-alquiler (GitHub Actions)"}


def get_json(url, intentos=4):
    ultimo = None
    for i in range(intentos):
        if i:
            time.sleep(2 ** i)
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            ultimo = e
    raise RuntimeError(f"{url}: {ultimo}")


def bcra_serie(id_variable, desde):
    """Devuelve {fecha: valor} paginando la API v4 del BCRA."""
    hasta = date.today().isoformat()
    valores, offset = {}, 0
    while True:
        j = get_json(f"{BCRA}{id_variable}?desde={desde}&hasta={hasta}&limit=1000&offset={offset}")
        det = (j.get("results") or [{}])[0].get("detalle") or []
        for x in det:
            valores[x["fecha"][:10]] = float(x["valor"])
        total = j.get("metadata", {}).get("resultset", {}).get("count", len(det))
        offset += len(det)
        if not det or offset >= total:
            return valores


def icl():
    valores = bcra_serie(40, "2020-07-01")
    if len(valores) < 100:
        raise RuntimeError("ICL: muy pocos valores")
    return {"fuente": "BCRA, variable 40", "tipo": "indice_diario",
            "datos": dict(sorted(valores.items()))}


def ipc_indec():
    j = get_json("https://apis.datos.gob.ar/series/api/series/"
                 "?ids=148.3_INIVELNAL_DICI_M_26&format=json&limit=1000&start_date=2017-01-01")
    datos = {f[:7]: float(v) for f, v in j["data"] if v is not None}
    return {"fuente": "INDEC (datos.gob.ar)", "tipo": "indice_mensual", "datos": datos}


def ipc_bcra():
    valores = bcra_serie(27, "2017-01-01")
    return {"fuente": "BCRA, variable 27", "tipo": "variacion_mensual",
            "datos": {f[:7]: v for f, v in sorted(valores.items())}}


def ipc_argentinadatos():
    j = get_json("https://api.argentinadatos.com/v1/finanzas/indices/inflacion")
    datos = {x["fecha"][:7]: float(x["valor"]) for x in j if x["fecha"] >= "2017-01"}
    return {"fuente": "INDEC vía ArgentinaDatos", "tipo": "variacion_mensual", "datos": datos}


def guardar(nombre, contenido):
    ruta = DATA / nombre
    # Solo se reescribe si cambiaron los valores, para no generar commits vacíos
    try:
        anterior = json.loads(ruta.read_text())
        if anterior.get("datos") == contenido["datos"] and anterior.get("fuente") == contenido["fuente"]:
            print(f"{nombre}: sin cambios (último {max(contenido['datos'])})")
            return
    except (FileNotFoundError, ValueError):
        pass
    contenido["actualizado"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    ruta.write_text(json.dumps(contenido, ensure_ascii=False, separators=(",", ":")) + "\n")
    ultimo = max(contenido["datos"])
    print(f"{nombre}: {len(contenido['datos'])} valores, último {ultimo} ({contenido['fuente']})")


def main():
    DATA.mkdir(exist_ok=True)
    errores = 0
    try:
        guardar("icl.json", icl())
    except Exception as e:  # noqa: BLE001
        errores += 1
        print(f"ICL sin actualizar: {e}", file=sys.stderr)

    for fuente in (ipc_indec, ipc_bcra, ipc_argentinadatos):
        try:
            res = fuente()
            if len(res["datos"]) < 12:
                raise RuntimeError("muy pocos valores")
            guardar("ipc.json", res)
            break
        except Exception as e:  # noqa: BLE001
            print(f"IPC {fuente.__name__} falló: {e}", file=sys.stderr)
    else:
        errores += 1

    # REM: mediana de inflación esperada a 12 meses, usada para proyectar
    try:
        valores = bcra_serie(29, "2024-01-01")
        if not valores:
            raise RuntimeError("sin valores")
        guardar("rem.json", {"fuente": "BCRA, variable 29 (REM)", "tipo": "variacion_anual_esperada",
                             "datos": dict(sorted(valores.items()))})
    except Exception as e:  # noqa: BLE001
        print(f"REM sin actualizar: {e}", file=sys.stderr)

    # Si fallan las dos series no se marca error: queda la copia anterior
    # y la próxima ejecución lo vuelve a intentar.
    print("Listo" if not errores else f"Terminó con {errores} serie(s) sin actualizar")


if __name__ == "__main__":
    main()
