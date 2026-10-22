import flet as ft
from datetime import datetime


def main(page: ft.Page):
    page.title = "Мой проект на Flet"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1100
    page.window.height = 760
    page.padding = 0

    tasks = []
    notes = []

    title = ft.Text("Главная", size=28, weight=ft.FontWeight.BOLD)
    content = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    def show_message(message):
        page.open(ft.SnackBar(content=ft.Text(message)))

    def set_content(name, controls):
        title.value = name
        content.controls = controls
        page.update()

    def make_card(heading, description, icon):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(icon, size=28, color=ft.Colors.BLUE),
                                ft.Text(
                                    heading,
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ]
                        ),
                        ft.Text(description, color=ft.Colors.GREY_700),
                    ],
                    spacing=12,
                ),
                padding=20,
                width=260,
            )
        )

    def home_page():
        set_content(
            "Главная",
            [
                ft.Text(
                    "Добро пожаловать!",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text("Приложение для управления задачами и заметками."),
                ft.Row(
                    [
                        make_card(
                            "Задачи",
                            f"Всего задач: {len(tasks)}",
                            ft.Icons.CHECK_CIRCLE,
                        ),
                        make_card(
                            "Заметки",
                            f"Всего заметок: {len(notes)}",
                            ft.Icons.NOTE,
                        ),
                    ],
                    wrap=True,
                ),
                ft.Text(
                    "Быстрый старт",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Открыть задачи",
                            icon=ft.Icons.CHECKLIST,
                            on_click=lambda _: tasks_page(),
                        ),
                        ft.OutlinedButton(
                            "Открыть заметки",
                            icon=ft.Icons.EDIT_NOTE,
                            on_click=lambda _: notes_page(),
                        ),
                    ],
                    wrap=True,
                ),
            ],
        )

    def tasks_page():
        task_input = ft.TextField(
            label="Новая задача",
            hint_text="Например: прочитать документацию",
            expand=True,
        )
        task_list = ft.Column(spacing=8)

        def delete_task(index):
            if 0 <= index < len(tasks):
                tasks.pop(index)
                refresh_tasks()
                page.update()

        def refresh_tasks():
            task_list.controls.clear()

            if not tasks:
                task_list.controls.append(
                    ft.Text(
                        "Пока задач нет.",
                        color=ft.Colors.GREY_600,
                    )
                )
                return

            for index, task in enumerate(tasks):
                checkbox = ft.Checkbox(
                    label=task["text"],
                    value=task["done"],
                )

                def on_checkbox_change(event, item=task):
                    item["done"] = event.control.value
                    page.update()

                checkbox.on_change = on_checkbox_change

                delete_button = ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    tooltip="Удалить задачу",
                    on_click=lambda _, i=index: delete_task(i),
                )

                task_list.controls.append(
                    ft.Row(
                        [
                            checkbox,
                            ft.Container(expand=True),
                            delete_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )
                )

        def add_task(_):
            text = task_input.value.strip() if task_input.value else ""

            if not text:
                show_message("Введите текст задачи.")
                return

            tasks.append({"text": text, "done": False})
            task_input.value = ""
            refresh_tasks()
            page.update()

        def clear_completed(_):
            tasks[:] = [task for task in tasks if not task["done"]]
            refresh_tasks()
            page.update()
            show_message("Выполненные задачи удалены.")

        refresh_tasks()

        set_content(
            "Задачи",
            [
                ft.Row(
                    [
                        task_input,
                        ft.ElevatedButton(
                            "Добавить",
                            icon=ft.Icons.ADD,
                            on_click=add_task,
                        ),
                    ]
                ),
                ft.Row(
                    [
                        ft.Text(
                            "Мои задачи",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.TextButton(
                            "Удалить выполненные",
                            on_click=clear_completed,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                task_list,
            ],
        )

    def notes_page():
        note_title = ft.TextField(label="Заголовок заметки")
        note_text = ft.TextField(
            label="Текст заметки",
            multiline=True,
            min_lines=4,
            max_lines=8,
        )
        notes_list = ft.Column(spacing=10)

        def delete_note(index):
            if 0 <= index < len(notes):
                notes.pop(index)
                refresh_notes()
                page.update()

        def refresh_notes():
            notes_list.controls.clear()

            if not notes:
                notes_list.controls.append(
                    ft.Text(
                        "Заметок пока нет.",
                        color=ft.Colors.GREY_600,
                    )
                )
                return

            for index, note in enumerate(notes):
                notes_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(
                                                note["title"],
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                                expand=True,
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_OUTLINE,
                                                tooltip="Удалить заметку",
                                                on_click=lambda _, i=index: delete_note(i),
                                            ),
                                        ]
                                    ),
                                    ft.Text(note["text"]),
                                    ft.Text(
                                        note["date"],
                                        size=12,
                                        color=ft.Colors.GREY_600,
                                    ),
                                ],
                                spacing=8,
                            ),
                            padding=16,
                        )
                    )
                )

        def add_note(_):
            heading = note_title.value.strip() if note_title.value else ""
            body = note_text.value.strip() if note_text.value else ""

            if not heading or not body:
                show_message("Заполните заголовок и текст заметки.")
                return

            notes.append(
                {
                    "title": heading,
                    "text": body,
                    "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
                }
            )

            note_title.value = ""
            note_text.value = ""
            refresh_notes()
            page.update()
            show_message("Заметка сохранена.")

        refresh_notes()

        set_content(
            "Заметки",
            [
                note_title,
                note_text,
                ft.ElevatedButton(
                    "Сохранить заметку",
                    icon=ft.Icons.SAVE,
                    on_click=add_note,
                ),
                ft.Divider(),
                ft.Text(
                    "Сохранённые заметки",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                notes_list,
            ],
        )

    def settings_page():
        theme_switch = ft.Switch(
            label="Тёмная тема",
            value=page.theme_mode == ft.ThemeMode.DARK,
        )

        def change_theme(event):
            if event.control.value:
                page.theme_mode = ft.ThemeMode.DARK
            else:
                page.theme_mode = ft.ThemeMode.LIGHT

            page.update()

        theme_switch.on_change = change_theme

        set_content(
            "Настройки",
            [
                ft.Text(
                    "Настройки приложения",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                theme_switch,
                ft.Text(
                    "Задачи и заметки хранятся только до закрытия приложения."
                ),
            ],
        )

    def navigate(event):
        selected = event.control.selected_index

        if selected == 0:
            home_page()
        elif selected == 1:
            tasks_page()
        elif selected == 2:
            notes_page()
        elif selected == 3:
            settings_page()

    navigation = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Главная",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CHECKLIST_OUTLINED,
                selected_icon=ft.Icons.CHECKLIST,
                label="Задачи",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.NOTE_OUTLINED,
                selected_icon=ft.Icons.NOTE,
                label="Заметки",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Настройки",
            ),
        ],
        on_change=navigate,
    )

    page.add(
        ft.Row(
            [
                navigation,
                ft.VerticalDivider(width=1),
                ft.Column(
                    [
                        ft.Container(
                            content=title,
                            padding=20,
                        ),
                        ft.Divider(height=1),
                        ft.Container(
                            content=content,
                            expand=True,
                            padding=20,
                        ),
                    ],
                    expand=True,
                    spacing=0,
                ),
            ],
            expand=True,
            spacing=0,
        )
    )

    home_page()


ft.run(main)