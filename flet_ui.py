import sys
import os

venv_python = os.path.join(os.path.dirname(__file__), "venv", "bin", "python")
if sys.executable != venv_python and os.path.exists(venv_python):
    os.execv(venv_python, [venv_python] + sys.argv)

import flet as ft
from agente import ChatbotAgent


def main(page: ft.Page):
    page.title = "Chatbot Q-Learning"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.window.width = 900
    page.window.height = 800

    agente = ChatbotAgent()
    estado_actual = None
    accion_actual = None

    chat_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=4)
    log_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=2)

    like_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.THUMB_UP, size=20, color=ft.Colors.GREEN_700),
            ft.Text("  Like (+1)", color=ft.Colors.GREEN_700, weight=ft.FontWeight.BOLD),
        ]),
        padding=20,
        border_radius=10,
        animate=ft.Animation(400),
        visible=False,
        tooltip="Like (+1) - Ctrl+L",
        on_click=lambda e: procesar_recompensa(1),
    )
    dislike_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.THUMB_DOWN, size=20, color=ft.Colors.RED_700),
            ft.Text("  Dislike (-1)", color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD),
        ]),
        padding=20,
        border_radius=10,
        animate=ft.Animation(400),
        visible=False,
        tooltip="Dislike (-1) - Ctrl+D",
        on_click=lambda e: procesar_recompensa(-1),
    )

    msg_input = ft.TextField(
        hint_text="Escribe tu mensaje...",
        expand=True,
        border_radius=18,
        text_style=ft.TextStyle(size=14),
        on_submit=lambda e: enviar(e),
    )

    send_btn = ft.IconButton(
        icon=ft.Icons.SEND_ROUNDED,
        icon_size=24,
    )

    def agregar_mensaje(emisor: str, texto: str, es_usuario: bool = False):
        color = ft.Colors.BLUE_100 if es_usuario else ft.Colors.GREY_200
        align = ft.Alignment.CENTER_RIGHT if es_usuario else ft.Alignment.CENTER_LEFT
        chat_list.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(emisor, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                    ft.Text(texto, size=14, selectable=True),
                ]),
                bgcolor=color,
                border_radius=12,
                padding=10,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                alignment=align,
                width=page.width * 0.7 if page.width else 400,
            )
        )
        page.update()

    def mostrar_controles_feedback(mostrar: bool):
        like_btn.visible = mostrar
        dislike_btn.visible = mostrar
        if mostrar:
            like_btn.bgcolor = ft.Colors.GREEN_100
            dislike_btn.bgcolor = ft.Colors.RED_100
        else:
            like_btn.bgcolor = None
            dislike_btn.bgcolor = None
        page.update()

    def habilitar_input(habilitado: bool):
        msg_input.disabled = not habilitado
        send_btn.disabled = not habilitado
        page.update()

    def enviar(e=None):
        nonlocal estado_actual, accion_actual

        mensaje = msg_input.value.strip()
        if not mensaje:
            return

        agregar_mensaje("Tú", mensaje, es_usuario=True)
        msg_input.value = ""
        habilitar_input(False)

        estado_actual = agente.clasificar_estado(mensaje)
        accion_actual, metodo = agente.seleccionar_accion(estado_actual)

        agregar_mensaje("Bot", accion_actual)
        mostrar_controles_feedback(True)
        page.update()

    def procesar_recompensa(valor: int):
        nonlocal estado_actual, accion_actual

        mostrar_controles_feedback(False)

        log_f, log_r = agente.actualizar_aprendizaje(estado_actual, accion_actual, valor)
        etiqueta = "+1 (Like)" if valor == 1 else "-1 (Dislike)"
        agregar_log(f"Respuesta evaluada: {etiqueta}")
        agregar_log(log_f)
        agregar_log(log_r)
        actualizar_tabla_q()

        habilitar_input(True)
        msg_input.focus()

    send_btn.on_click = lambda e: enviar(e)

    def agregar_log(texto: str):
        log_list.controls.append(
            ft.Text(f"▸ {texto}", size=11, selectable=True, color=ft.Colors.GREY_700)
        )
        page.update()

    def on_keyboard(e: ft.KeyboardEvent):
        if e.ctrl and e.key.lower() == "l" and like_btn.visible:
            procesar_recompensa(1)
        elif e.ctrl and e.key.lower() == "d" and dislike_btn.visible:
            procesar_recompensa(-1)

    page.on_keyboard_event = on_keyboard

    tabla_q_view = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD, size=12))],
        rows=[],
        column_spacing=5,
        horizontal_margin=5,
        data_row_min_height=30,
        heading_row_height=32,
    )

    for acc in agente.acciones:
        col_id = acc[:2]
        tabla_q_view.columns.append(ft.DataColumn(
            ft.Text(col_id, weight=ft.FontWeight.BOLD, size=11),
            numeric=True,
        ))

    def actualizar_tabla_q():
        tabla_q_view.rows.clear()
        for estado, acciones_valores in agente.tabla_q.items():
            celdas = [ft.DataCell(ft.Text(estado))]
            for acc in agente.acciones:
                valor = acciones_valores[acc]
                celdas.append(ft.DataCell(ft.Text(f"{valor:.4f}")))
            tabla_q_view.rows.append(ft.DataRow(cells=celdas))
        page.update()

    actualizar_tabla_q()

    tabla_q_container = ft.Container(
        content=ft.Column([
            ft.Text("Tabla Q", size=13, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=tabla_q_view,
                border_radius=8,
            ),
        ]),
        padding=15,
        bgcolor=ft.Colors.GREY_100,
        border_radius=ft.BorderRadius(15, 15, 0, 0),
        animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
    )

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Text("Chatbot Q-Learning", size=18, weight=ft.FontWeight.BOLD),
                    ], alignment=ft.MainAxisAlignment.START),
                    padding=ft.Padding(left=15, right=5, top=8, bottom=8),
                    bgcolor=ft.Colors.PRIMARY_CONTAINER,
                ),
                ft.Row([
                    ft.Container(
                        content=chat_list,
                        expand=True,
                        padding=10,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Tabla Q", size=14, weight=ft.FontWeight.BOLD),
                            ft.Divider(height=8),
                            ft.Column(
                                [tabla_q_view],
                                scroll=ft.ScrollMode.AUTO,
                                expand=True,
                            ),
                            ft.Divider(height=8),
                            ft.Text("Log", size=14, weight=ft.FontWeight.BOLD),
                            log_list,
                        ]),
                        width=320,
                        padding=15,
                        bgcolor=ft.Colors.GREY_100 if page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.GREY_900,
                    ),
                ], expand=True),
                ft.Container(
                    content=ft.Column([
                        ft.Row(
                            [msg_input, send_btn],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            [like_btn, dislike_btn],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ]),
                    padding=ft.Padding(left=10, right=10, top=5, bottom=10),
                ),
            ]),
            expand=True,
        )
    )

    agregar_log("Sistema inicializado. ¡Escribe un mensaje!")


if __name__ == "__main__":
    ft.run(main)
