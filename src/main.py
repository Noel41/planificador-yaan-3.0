import json
import os
from datetime import datetime
import flet as ft


def obtener_directorio_datos() -> str:
    """Devuelve una carpeta escribible, válida tanto en escritorio como en Android."""
    base_dir = os.getenv("FLET_APP_STORAGE_DATA")
    if base_dir:
        dir_datos = os.path.join(base_dir, "app_planificador")
    else:
        dir_datos = os.path.join(os.path.expanduser("~"), ".app_planificador")
    os.makedirs(dir_datos, exist_ok=True)
    return dir_datos


def parse_fecha(fecha_str: str):
    """Convierte un string de fecha en objeto date soportando varios formatos."""
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(fecha_str.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Formato no válido: {fecha_str}")


class TabActividades(ft.Column):
    """Pestaña que gestiona las actividades de un proyecto."""

    def __init__(self, page: ft.Page, nombre_proyecto: str):
        super().__init__(expand=True, spacing=10)
        self.app_page = page
        self.nombre_proyecto = nombre_proyecto
        self.archivo_json = (
            f"actividades_{nombre_proyecto.lower().replace(' ', '_')}.json"
        )
        self.actividades = self.cargar_actividades()

        self.txt_nueva = ft.TextField(
            hint_text="Nueva actividad...", expand=True, dense=True
        )
        self.txt_fecha = ft.TextField(
            hint_text="DD/MM/YYYY",
            value=datetime.now().strftime("%d/%m/%Y"),
            width=140,
            dense=True,
        )
        self.lv_actividades = ft.ListView(expand=True, spacing=6, padding=10)

        self.controls = [
            ft.Container(
                content=ft.Row(
                    [
                        self.txt_nueva,
                        self.txt_fecha,
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE,
                            icon_color=ft.Colors.BLUE_600,
                            icon_size=32,
                            tooltip="Añadir Actividad",
                            on_click=self.agregar_actividad,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=10,
            ),
            ft.Divider(height=1),
            self.lv_actividades,
        ]
        self.actualizar_lista()

    # ---------- Persistencia ----------
    def obtener_ruta_json(self) -> str:
        return os.path.join(obtener_directorio_datos(), self.archivo_json)

    def cargar_actividades(self):
        try:
            with open(self.obtener_ruta_json(), "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def guardar_actividades(self):
        try:
            with open(self.obtener_ruta_json(), "w", encoding="utf-8") as f:
                json.dump(self.actividades, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.app_page.open(ft.SnackBar(ft.Text(f"Error al guardar: {e}")))

    # ---------- Acciones ----------
    def agregar_actividad(self, e):
        texto = (self.txt_nueva.value or "").strip()
        fecha_str = (self.txt_fecha.value or "").strip()

        if not texto:
            self.app_page.open(
                ft.SnackBar(ft.Text("Escribe una descripción para la actividad."))
            )
            return

        try:
            fecha = parse_fecha(fecha_str)
            hoy = datetime.now().date()
            self.actividades.append(
                {
                    "texto": texto,
                    "completada": False,
                    "fecha": fecha.strftime("%d/%m/%Y"),
                    "dias_restantes": (fecha - hoy).days,
                }
            )
            self.txt_nueva.value = ""
            self.guardar_actividades()
            self.actualizar_lista()
            self.app_page.update()
            self.app_page.open(
                ft.SnackBar(ft.Text("Actividad añadida correctamente."))
            )
        except ValueError:
            self.app_page.open(
                ft.SnackBar(ft.Text("Formato de fecha inválido (Use DD/MM/YYYY)"))
            )

    def cambiar_estado(self, index: int, val: bool):
        self.actividades[index]["completada"] = val
        self.guardar_actividades()
        self.actualizar_lista()
        self.app_page.update()

    def eliminar_actividad(self, index: int):
        del self.actividades[index]
        self.guardar_actividades()
        self.actualizar_lista()
        self.app_page.update()

    def editar_actividad(self, index: int):
        act = self.actividades[index]
        input_edit = ft.TextField(value=act["texto"], expand=True)

        def guardar_edit(e):
            if (input_edit.value or "").strip():
                act["texto"] = input_edit.value.strip()
                self.guardar_actividades()
                self.actualizar_lista()
                dlg.open = False
                self.app_page.update()

        def cancelar_edit(e):
            dlg.open = False
            self.app_page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Editar Descripción"),
            content=input_edit,
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar_edit),
                ft.ElevatedButton("Guardar", on_click=guardar_edit),
            ],
        )
        self.app_page.open(dlg)

    # ---------- Render ----------
    def actualizar_lista(self):
        self.lv_actividades.controls.clear()
        hoy = datetime.now().date()

        for idx, act in enumerate(self.actividades):
            color = (
                ft.Colors.GREEN_600
                if act.get("completada")
                else ft.Colors.BLACK
            )
            subtexto = ""

            if act.get("fecha"):
                try:
                    fecha = parse_fecha(act["fecha"])
                    dias = (fecha - hoy).days
                    act["dias_restantes"] = dias

                    if not act.get("completada"):
                        if dias < 0:
                            color = ft.Colors.RED_600
                            subtexto = (
                                f"VENCIDA ({abs(dias)}d de retraso) - "
                                f"📅 {act['fecha']}"
                            )
                        elif dias <= 3:
                            color = ft.Colors.RED_500
                            subtexto = f"¡Urgente! Quedan {dias} días - 📅 {act['fecha']}"
                        elif dias <= 7:
                            color = ft.Colors.ORANGE_700
                            subtexto = f"Próxima: Quedan {dias} días - 📅 {act['fecha']}"
                        else:
                            subtexto = f"Quedan {dias} días - 📅 {act['fecha']}"
                    else:
                        subtexto = f"Completada - 📅 {act['fecha']}"
                except Exception:
                    subtexto = "Fecha no válida"

            weight = (
                ft.FontWeight.BOLD
                if not act.get("completada")
                else ft.FontWeight.NORMAL
            )

            self.lv_actividades.controls.append(
                ft.ListTile(
                    leading=ft.Checkbox(
                        value=act.get("completada", False),
                        on_change=lambda e, i=idx: self.cambiar_estado(
                            i, e.control.value
                        ),
                    ),
                    title=ft.Text(act["texto"], color=color, weight=weight),
                    subtitle=ft.Text(subtexto, size=12),
                    trailing=ft.Row(
                        [
                            ft.IconButton(
                                ft.Icons.EDIT,
                                icon_size=20,
                                on_click=lambda e, i=idx: self.editar_actividad(i),
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                icon_size=20,
                                icon_color=ft.Colors.RED_400,
                                on_click=lambda e, i=idx: self.eliminar_actividad(i),
                            ),
                        ],
                        width=90,
                        alignment=ft.MainAxisAlignment.END,
                    ),
                )
            )


# ==================== APP PRINCIPAL ====================

def main(page: ft.Page):
    page.title = "PLANIFICADOR YAAN"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    ruta_config = os.path.join(obtener_directorio_datos(), "config_proyectos.json")

    def cargar_proyectos():
        try:
            with open(ruta_config, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    return data
        except Exception:
            pass
        return ["Trabajo de Grado", "Ingeniería Electrónica", "General"]

    def guardar_proyectos(projs):
        try:
            with open(ruta_config, "w", encoding="utf-8") as f:
                json.dump(projs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            page.open(ft.SnackBar(ft.Text(f"Error al guardar proyectos: {e}")))

    proyectos = cargar_proyectos()
    tabs_holder = ft.Container(expand=True)

    def construir_tabs():
        tabs_holder.content = ft.Tabs(
            selected_index=0,
            expand=True,
            tabs=[
                ft.Tab(
                    text=p,
                    icon=ft.Icons.FOLDER,
                    content=TabActividades(page, p),
                )
                for p in proyectos
            ],
        )
        page.update()

    def crear_proyecto(e):
        txt_nombre = ft.TextField(hint_text="Nombre del trabajo...")

        def confirmar(e_conf):
            val = (txt_nombre.value or "").strip()
            if val and val not in proyectos:
                proyectos.append(val)
                guardar_proyectos(proyectos)
                construir_tabs()
                dlg.open = False
                page.update()

        def cancelar(e_canc):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("Nuevo Trabajo"),
            content=txt_nombre,
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton("Crear", on_click=confirmar),
            ],
        )
        page.open(dlg)

    def eliminar_proyecto_actual(e):
        if len(proyectos) <= 1:
            page.open(ft.SnackBar(ft.Text("Debes mantener al menos un trabajo.")))
            return

        idx = tabs_holder.content.selected_index or 0
        nombre = proyectos[idx]
        proyectos.pop(idx)
        guardar_proyectos(proyectos)
        construir_tabs()
        page.open(ft.SnackBar(ft.Text(f"Se eliminó '{nombre}'")))

    page.appbar = ft.AppBar(
        title=ft.Text("PLANIFICADOR YAAN"),
        center_title=False,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        actions=[
            ft.IconButton(
                ft.Icons.CREATE_NEW_FOLDER,
                tooltip="Nuevo Trabajo",
                on_click=crear_proyecto,
            ),
            ft.IconButton(
                ft.Icons.DELETE_SWEEP,
                tooltip="Eliminar Trabajo",
                on_click=eliminar_proyecto_actual,
            ),
        ],
    )

    page.add(tabs_holder)
    construir_tabs()


if __name__ == "__main__":
    ft.app(target=main)
