import flet as ft
from datetime import datetime
import asyncio
from dataclasses import dataclass
from simulator import SerialPortSimulator, WeightData


@dataclass
class WeightRecord:
    weight: float
    timestamp: datetime


class WeighingApp:
    def __init__(self):
        self.serial_simulator = SerialPortSimulator()
        self.weight_records: list[WeightRecord] = []
        self.display_text = ft.Text(
            "0.00",
            size=72,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREEN_400,
            font_family="Consolas, Courier New, monospace"
        )
        self.start_button = ft.ElevatedButton(
            "开始称重",
            on_click=self.on_start_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                padding=20,
            ),
            width=150,
            height=50
        )
        self.confirm_button = ft.ElevatedButton(
            "确定",
            on_click=self.on_confirm_click,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE,
                padding=20,
            ),
            width=150,
            height=50,
            disabled=True
        )
        self.weight_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("序号", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("重量 (kg)", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("时间", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_300),
        )
        self.page = None

    def on_weight_data(self, data: WeightData):
        if self.page:
            self.display_text.value = f"{data.weight:.2f}"
            if data.is_stable:
                self.display_text.color = ft.Colors.GREEN_400
                self.confirm_button.disabled = False
                self.start_button.disabled = False
            else:
                if int(data.timestamp * 10) % 2 == 0:
                    self.display_text.color = ft.Colors.GREEN_300
                else:
                    self.display_text.color = ft.Colors.GREEN_500
            self.page.update()

    async def on_start_click(self, e):
        self.start_button.disabled = True
        self.confirm_button.disabled = True
        self.display_text.color = ft.Colors.GREEN_500
        self.page.update()

        self.serial_simulator.weight_simulator.add_callback(self.on_weight_data)

        target_weight = 1234.56
        self.serial_simulator.start_weighing(target_weight)
        await self.serial_simulator.weight_simulator.simulate_weighing_process()

    def on_confirm_click(self, e):
        stable_weight = self.serial_simulator.weight_simulator.get_current_weight()
        record = WeightRecord(
            weight=stable_weight,
            timestamp=datetime.now()
        )
        self.weight_records.append(record)
        self.update_table()
        self.confirm_button.disabled = True
        self.display_text.value = "0.00"
        self.display_text.color = ft.Colors.GREEN_400
        self.page.update()

    def update_table(self):
        self.weight_table.rows.clear()
        for idx, record in enumerate(self.weight_records, start=1):
            time_str = record.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            self.weight_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(idx))),
                        ft.DataCell(ft.Text(f"{record.weight:.2f}")),
                        ft.DataCell(ft.Text(time_str)),
                    ]
                )
            )

    def build(self, page: ft.Page):
        self.page = page
        page.title = "称重传感器数据采集系统"
        page.window_width = 900
        page.window_height = 700
        page.window_resizable = True
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO

        display_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "重量显示",
                        size=16,
                        color=ft.Colors.GREY_300,
                    ),
                    self.display_text,
                    ft.Text(
                        "kg",
                        size=24,
                        color=ft.Colors.GREEN_400,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
            bgcolor=ft.Colors.BLACK,
            border_radius=15,
            padding=30,
            expand=True,
            height=200,
        )

        button_column = ft.Column(
            [
                self.start_button,
                self.confirm_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        top_row = ft.Row(
            [
                display_container,
                button_column,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
        )

        table_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "称重记录表",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(),
                    ft.ListView(
                        [self.weight_table],
                        expand=True,
                        auto_scroll=True,
                    ),
                ],
                expand=True,
            ),
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            padding=20,
            expand=True,
        )

        main_column = ft.Column(
            [
                top_row,
                ft.Divider(height=30),
                table_container,
            ],
            expand=True,
            spacing=20,
        )

        page.add(main_column)


def main():
    app = WeighingApp()
    ft.app(target=app.build)


if __name__ == "__main__":
    main()
