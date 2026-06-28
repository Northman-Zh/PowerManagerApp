from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox
)

from services.power_service import (
    shutdown,
    cancel_shutdown
)


class PowerWidget(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel(
            "Питание ПК"
        )

        layout.addWidget(
            title
        )

        self.minutes = QSpinBox()

        self.minutes.setRange(
            1,
            1440
        )

        self.minutes.setValue(
            60
        )

        layout.addWidget(
            self.minutes
        )

        buttons = QHBoxLayout()

        start_btn = QPushButton(
            "Выключить"
        )

        cancel_btn = QPushButton(
            "Отменить"
        )

        start_btn.clicked.connect(
            self.start_shutdown
        )

        cancel_btn.clicked.connect(
            self.cancel_action
        )

        buttons.addWidget(
            start_btn
        )

        buttons.addWidget(
            cancel_btn
        )

        layout.addLayout(
            buttons
        )

        self.setLayout(
            layout
        )


    def start_shutdown(
        self
    ):

        minutes = (
            self.minutes.value()
        )

        shutdown(
            minutes
        )

        QMessageBox.information(
            self,
            "Таймер",
            f"ПК выключится через {minutes} минут"
        )


    def cancel_action(
        self
    ):

        cancel_shutdown()

        QMessageBox.information(
            self,
            "Отмена",
            "Выключение отменено"
        )