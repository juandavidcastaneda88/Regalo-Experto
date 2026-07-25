from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path
from threading import Lock
from typing import Any


class HistorialService:
    def __init__(self, ruta: str | Path, maximo: int = 500):
        self.ruta = Path(ruta)
        self.maximo = maximo
        self._lock = Lock()
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        if not self.ruta.exists():
            self.ruta.write_text("[]", encoding="utf-8")

    def listar(self) -> list[dict[str, Any]]:
        with self._lock:
            try:
                datos = json.loads(self.ruta.read_text(encoding="utf-8"))
                return datos if isinstance(datos, list) else []
            except (OSError, json.JSONDecodeError):
                return []

    def agregar(self, registro: dict[str, Any]) -> None:
        with self._lock:
            historial = self._leer_sin_lock()
            historial.insert(0, registro)
            self._escribir_atomico(historial[: self.maximo])

    def limpiar(self) -> None:
        with self._lock:
            self._escribir_atomico([])

    def estadisticas(self, historial: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        datos = historial if historial is not None else self.listar()
        puntuaciones: list[int] = []
        nombres: list[str] = []
        for registro in datos:
            mejor = (registro.get("resultado", {}).get("recomendaciones") or [None])[0]
            if mejor:
                puntuaciones.append(int(mejor.get("porcentaje", 0)))
                nombres.append(str(mejor.get("nombre", "")))
        frecuente = Counter(nombres).most_common(1)
        return {
            "consultas": len(datos),
            "afinidad_promedio": round(sum(puntuaciones) / len(puntuaciones)) if puntuaciones else 0,
            "regalo_mas_recomendado": frecuente[0][0] if frecuente else "—",
        }

    def _leer_sin_lock(self) -> list[dict[str, Any]]:
        try:
            datos = json.loads(self.ruta.read_text(encoding="utf-8"))
            return datos if isinstance(datos, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def _escribir_atomico(self, datos: list[dict[str, Any]]) -> None:
        temporal = self.ruta.with_suffix(self.ruta.suffix + ".tmp")
        temporal.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temporal, self.ruta)
