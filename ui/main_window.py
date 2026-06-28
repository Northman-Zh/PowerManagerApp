from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSlider,
    QSpinBox,
    QMessageBox,
    QCheckBox,
    QInputDialog,
)

from PySide6.QtCore import (
    Qt,
    QTimer,
)

from services.power_service import (
    shutdown,
    cancel_shutdown,
)

from services.brightness_service import (
    get_monitors,
    get_current_brightness,
    set_all_brightness,
    set_monitor_brightness,
)

from services.settings_service import (
    load_settings,
    save_settings,
)

from services.profile_service import (
    save_profile,
    load_profiles,
)

from widgets.power_widget import PowerWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = (
    load_settings()
)

        self.setWindowTitle(
            "Power & Display Manager"
        )

        self.resize(
    self.settings[
        "window_width"
    ],
    self.settings[
        "window_height"
    ]
)

        self.monitor_widgets = []
        self.monitor_sliders = []
        self.monitor_labels = []

        self.pending_updates = {}

        # Таймер для плавности
        self.update_interval = (
    self.settings[
        "update_interval"
    ]
)

        self.update_timer = QTimer()
        self.update_timer.setInterval(
        self.update_interval
        )

        self.update_timer.timeout.connect(
        self.apply_brightness
        )

        self.main_layout = QVBoxLayout()

        # ==================
        # Заголовок
        # ==================
        title = QLabel(
            "Power & Display Manager"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        self.main_layout.addWidget(
            title
        )

        self.main_layout.addWidget(
            PowerWidget()
        )

        # ==================
        # Мониторы
        # ==================
        brightness_title = QLabel(
            "Яркость мониторов"
        )
        
        
        self.main_layout.addWidget(
            brightness_title
        )

        self.link_checkbox = (
            QCheckBox(
                "Связать яркость"
            )
        )

        self.link_checkbox.setChecked(
    self.settings[
        "linked_brightness"
    ]
)

        self.link_checkbox.stateChanged.connect(
            self.rebuild_monitor_ui
        )

        self.main_layout.addWidget(
            self.link_checkbox
        )

        self.monitors_layout = (
            QVBoxLayout()
        )

        self.main_layout.addLayout(
                self.monitors_layout
            )

        self.rebuild_monitor_ui()

            # ==================
            # Настройки
            # ==================
        settings_title = QLabel(
                "Настройки"
            )

        self.main_layout.addWidget(
                settings_title
            )

        self.response_label = QLabel(
                f"Отклик яркости: "
                f"{self.update_interval} мс"
            )

        self.main_layout.addWidget(
                self.response_label
            )

        self.response_slider = (
                QSlider(
                    Qt.Horizontal
                )
            )

        self.response_slider.setRange(
                10,
                100
            )

        self.response_slider.setValue(
                self.update_interval
            )

        self.response_slider.valueChanged.connect(
                self.change_response_time
            )

        self.main_layout.addWidget(
                self.response_slider
            )
        # ==================
        # Профили
        # ==================
        profiles_title = QLabel(
            "Профили яркости"
        )

        self.main_layout.addWidget(
            profiles_title
        )

        save_profile_btn = (
            QPushButton(
                "Сохранить профиль"
            )
        )

        save_profile_btn.clicked.connect(
            self.create_profile
        )

        self.main_layout.addWidget(
            save_profile_btn
        )

        self.profiles_layout = (
            QVBoxLayout()
        )

        self.main_layout.addLayout(
            self.profiles_layout
        )

        self.rebuild_profiles_ui()

        self.setLayout(
                self.main_layout
            )

    # ==================
    # Перестройка UI
    # ==================
    def rebuild_monitor_ui(self):

        while (
            self.monitors_layout.count()
        ):
            item = (
                self.monitors_layout
                .takeAt(0)
            )

            widget = item.widget()

            if widget:
                widget.deleteLater()

        self.monitor_sliders.clear()
        self.monitor_labels.clear()

        brightness_list = (
            get_current_brightness()
        )

        monitors = get_monitors()

        # ----------------
        # Один ползунок
        # ----------------
        if (
            self.link_checkbox
            .isChecked()
        ):

            current = (
                brightness_list[0]
            )

            label = QLabel(
                "Общая яркость"
            )

            self.monitors_layout.addWidget(
                label
            )

            slider = QSlider(
                Qt.Horizontal
            )

            slider.setRange(0, 100)
            slider.setValue(current)

            value_label = QLabel(
                f"{current}%"
            )

            slider.valueChanged.connect(
                lambda value:
                self.queue_linked_brightness(
                    value,
                    value_label
                )
            )

            slider.sliderReleased.connect(
                self.force_apply
            )

            self.monitor_sliders.append(
                slider
            )

            self.monitor_labels.append(
                value_label
            )

            self.monitors_layout.addWidget(
                slider
            )

            self.monitors_layout.addWidget(
                value_label
            )

        # ----------------
        # Несколько
        # ----------------
        else:

            for index, monitor in enumerate(
                monitors
            ):

                monitor_name = (
                    monitor.get(
                        "name",
                        f"Монитор {index + 1}"
                    )
                )

                label = QLabel(
                    monitor_name
                )

                self.monitors_layout.addWidget(
                    label
                )

                slider = QSlider(
                    Qt.Horizontal
                )

                slider.setRange(0, 100)

                current = (
                    brightness_list[
                        min(
                            index,
                            len(
                                brightness_list
                            ) - 1
                        )
                    ]
                )

                slider.setValue(
                    current
                )

                value_label = QLabel(
                    f"{current}%"
                )

                slider.valueChanged.connect(
                    lambda value,
                    idx=index,
                    lbl=value_label:
                    self.queue_monitor_brightness(
                        idx,
                        value,
                        lbl
                    )
                )

                slider.sliderReleased.connect(
                    self.force_apply
                )

                self.monitor_sliders.append(
                    slider
                )

                self.monitor_labels.append(
                    value_label
                )

                self.monitors_layout.addWidget(
                    slider
                )

                self.monitors_layout.addWidget(
                    value_label
                )

    # ==================
    # Очередь обновлений
    # ==================
    def queue_linked_brightness(
        self,
        value,
        label
    ):
        label.setText(
            f"{value}%"
        )

        self.pending_updates[
            "all"
        ] = value

        if (
            not self.update_timer
            .isActive()
        ):
            self.update_timer.start()

    def queue_monitor_brightness(
        self,
        monitor_index,
        value,
        label
    ):
        label.setText(
            f"{value}%"
        )

        self.pending_updates[
            monitor_index
        ] = value

        if (
            not self.update_timer
            .isActive()
        ):
            self.update_timer.start()

    def apply_brightness(self):

        if (
            "all"
            in self.pending_updates
        ):

            value = (
                self.pending_updates[
                    "all"
                ]
            )

            set_all_brightness(
                value
            )

        else:

            for (
                monitor,
                value
            ) in (
                self.pending_updates
                .items()
            ):

                set_monitor_brightness(
                    value,
                    monitor
                )

        self.pending_updates.clear()

    def force_apply(self):
        self.apply_brightness()

    # ==================
    # Питание
    # ==================
    def start_shutdown(self):

        minutes = (
            self.minutes.value()
        )

        shutdown(minutes)

        QMessageBox.information(
            self,
            "Таймер установлен",
            f"ПК выключится через {minutes} минут"
        )

    def cancel_action(self):

        cancel_shutdown()

        QMessageBox.information(
            self,
            "Отменено",
            "Выключение отменено"
        )

    def change_response_time(
        self,
        value
    ):
        self.update_interval = value

        self.update_timer.setInterval(
            value
        )

        self.response_label.setText(
            f"Отклик яркости: "
            f"{value} мс"
        )

    def rebuild_profiles_ui(
        self
    ):

        while (
            self.profiles_layout
            .count()
        ):

            item = (
                self.profiles_layout
                .takeAt(0)
            )

            widget = item.widget()

            if widget:
                widget.deleteLater()

        profiles = (
            load_profiles()
        )

        for (
            profile_name,
            values
        ) in profiles.items():

            button = QPushButton(
                profile_name
            )

            button.clicked.connect(
                lambda checked=False,
                vals=values:
                self.apply_profile(
                    vals
                )
            )

            self.profiles_layout.addWidget(
                button
            )

    def create_profile(
        self
    ):

        name, ok = (
            QInputDialog.getText(
                self,
                "Новый профиль",
                "Введите имя профиля:"
            )
        )

        if (
            not ok
            or not name.strip()
        ):
            return

        brightness = (
            get_current_brightness()
        )

        save_profile(
            name.strip(),
            brightness
        )

        self.rebuild_profiles_ui()

    def apply_profile(
        self,
        brightness_values
    ):

        monitors = (
            get_monitors()
        )

        for index in range(
            min(
                len(monitors),
                len(
                    brightness_values
                )
            )
        ):

            set_monitor_brightness(
                brightness_values[
                    index
                ],
                index
            )

        self.rebuild_monitor_ui()

    # ==================
    # Питание
    # ==================
    

    def closeEvent(
        self,
        event
    ):

        settings = {
            "update_interval":
            self.update_interval,

            "linked_brightness":
            self.link_checkbox
            .isChecked(),

            "window_width":
            self.width(),

            "window_height":
            self.height(),
        }

        save_settings(
            settings
        )

        event.accept()