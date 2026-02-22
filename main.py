"""PyQt GUI."""

import sys

import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from ops.edge_ops import edge_canny, edge_prewitt, edge_roberts, edge_sobel
from ops.filter_ops import apply_average_filter, apply_gaussian_filter, apply_median_filter
from ops.io_ops import read_image_bgr, to_gray
from ops.noise_ops import add_gaussian_noise, add_salt_pepper_noise, add_uniform_noise


class ImagePanel(QtWidgets.QLabel):
    # Simple image preview widget.
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(280, 200)
        self.setText(title)
        self.setStyleSheet("QLabel{border:1px solid #444;}")
        self._image = None

    def set_image(self, image: np.ndarray) -> None:
        # Convert NumPy image to QPixmap and render it.
        if image is None:
            self.setText("(no preview)")
            self.setPixmap(QtGui.QPixmap())
            self._image = None
            return
        self._image = image
        if len(image.shape) == 2:
            qimage = QtGui.QImage(
                image.data, image.shape[1], image.shape[0], image.strides[0], QtGui.QImage.Format_Grayscale8
            )
        else:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            qimage = QtGui.QImage(
                rgb.data, rgb.shape[1], rgb.shape[0], rgb.strides[0], QtGui.QImage.Format_RGB888
            )
        pixmap = QtGui.QPixmap.fromImage(qimage)
        self.setPixmap(pixmap.scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def resizeEvent(self, event) -> None:
        # Re-scale preview when the widget size changes.
        if self._image is not None:
            self.set_image(self._image)
        super().resizeEvent(event)


class MainWindow(QtWidgets.QMainWindow):
    # Main application window with tabs for each task stage.
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Computer Vision Task 1")
        self.setWindowIcon(QtGui.QIcon("computer-vision-icon.jpg"))
        self.resize(1200, 720)
        self.setStyleSheet(self._build_theme())

        # Cached images for each stage in the pipeline.
        self.original_bgr = None
        self.gray = None
        self.noisy = None
        self.filtered = None

        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        self._build_tab_load()
        self._build_tab_noise()
        self._build_tab_filters()
        self._build_tab_edges()

    def _build_tab_load(self) -> None:
        # Build the Load tab UI.
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        buttons = QtWidgets.QHBoxLayout()
        self.btn_open = QtWidgets.QPushButton("Open Image")
        self.btn_open.clicked.connect(self.open_image)
        self.btn_save = QtWidgets.QPushButton("Save Edited")
        self.btn_save.clicked.connect(self.save_edited)
        self.save_target = QtWidgets.QComboBox()
        self.save_target.addItems(
            [
                "Gray (original)",
                "Original (RGB)",
                "Noisy",
                "Filtered",
                "Edges (Magnitude)",
                "Edges (X)",
                "Edges (Y)",
            ]
        )
        self.save_target.setToolTip("Choose which image to save. Output is always saved as grayscale.")
        buttons.addWidget(self.btn_open)
        buttons.addWidget(self.btn_save)
        buttons.addWidget(self.save_target)
        buttons.addStretch()

        images = QtWidgets.QHBoxLayout()
        self.panel_original = ImagePanel("Original (RGB)")
        self.panel_gray = ImagePanel("Gray")
        images.addWidget(self.panel_original)
        images.addWidget(self.panel_gray)

        layout.addLayout(buttons)
        layout.addLayout(images)
        self.tabs.addTab(widget, "Load")

    def _build_tab_noise(self) -> None:
        # Build the Noise tab UI.
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        form = QtWidgets.QFormLayout()
        self.noise_type = QtWidgets.QComboBox()
        self.noise_type.addItems(["Uniform", "Gaussian", "Salt & Pepper"])
        self.noise_type.currentIndexChanged.connect(self._update_noise_controls)

        self.uniform_low = QtWidgets.QSpinBox()
        self.uniform_low.setRange(-100, 100)
        self.uniform_low.setValue(-20)
        self.uniform_high = QtWidgets.QSpinBox()
        self.uniform_high.setRange(-100, 100)
        self.uniform_high.setValue(20)

        self.gauss_mean = QtWidgets.QDoubleSpinBox()
        self.gauss_mean.setRange(-50.0, 50.0)
        self.gauss_mean.setValue(0.0)
        self.gauss_sigma = QtWidgets.QDoubleSpinBox()
        self.gauss_sigma.setRange(1.0, 100.0)
        self.gauss_sigma.setValue(15.0)

        self.sp_amount = QtWidgets.QDoubleSpinBox()
        self.sp_amount.setRange(0.0, 0.5)
        self.sp_amount.setSingleStep(0.01)
        self.sp_amount.setValue(0.05)
        self.sp_ratio = QtWidgets.QDoubleSpinBox()
        self.sp_ratio.setRange(0.0, 1.0)
        self.sp_ratio.setSingleStep(0.05)
        self.sp_ratio.setValue(0.5)

        form.addRow("Noise type", self.noise_type)
        form.addRow("Uniform low", self.uniform_low)
        form.addRow("Uniform high", self.uniform_high)
        form.addRow("Gaussian mean", self.gauss_mean)
        form.addRow("Gaussian sigma", self.gauss_sigma)
        form.addRow("S&P amount", self.sp_amount)
        form.addRow("S&P salt ratio", self.sp_ratio)

        self.btn_apply_noise = QtWidgets.QPushButton("Apply Noise")
        self.btn_apply_noise.clicked.connect(self.apply_noise)

        images = QtWidgets.QHBoxLayout()
        self.panel_noise_in = ImagePanel("Input")
        self.panel_noisy = ImagePanel("Noisy")
        images.addWidget(self.panel_noise_in)
        images.addWidget(self.panel_noisy)

        layout.addLayout(form)
        layout.addWidget(self.btn_apply_noise)
        layout.addLayout(images)
        self.tabs.addTab(widget, "Noise")
        self._update_noise_controls()

    def _build_tab_filters(self) -> None:
        # Build the Filters tab UI.
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        form = QtWidgets.QFormLayout()
        self.filter_source = QtWidgets.QComboBox()
        self.filter_source.addItems(["Original", "Noisy (if available)"])

        self.filter_type = QtWidgets.QComboBox()
        self.filter_type.addItems(["Average", "Gaussian", "Median"])
        self.filter_type.currentIndexChanged.connect(self._update_filter_controls)

        self.filter_ksize = QtWidgets.QSpinBox()
        self.filter_ksize.setRange(1, 31)
        self.filter_ksize.setSingleStep(2)
        self.filter_ksize.setValue(3)

        self.filter_sigma = QtWidgets.QDoubleSpinBox()
        self.filter_sigma.setRange(0.1, 50.0)
        self.filter_sigma.setValue(1.5)

        self.filter_source_status = QtWidgets.QLabel("Noisy image: not available")
        self.filter_source_status.setStyleSheet("color:#5c554a;")

        form.addRow("Filter input", self.filter_source)
        form.addRow("Filter type", self.filter_type)
        form.addRow("Kernel size", self.filter_ksize)
        form.addRow("Gaussian sigma", self.filter_sigma)

        self.btn_apply_filter = QtWidgets.QPushButton("Apply Filter")
        self.btn_apply_filter.clicked.connect(self.apply_filter)

        images = QtWidgets.QHBoxLayout()
        self.panel_filter_in = ImagePanel("Input")
        self.panel_filtered = ImagePanel("Filtered")
        images.addWidget(self.panel_filter_in)
        images.addWidget(self.panel_filtered)

        layout.addLayout(form)
        layout.addWidget(self.filter_source_status)
        layout.addWidget(self.btn_apply_filter)
        layout.addLayout(images)
        self.tabs.addTab(widget, "Filters")
        self._update_filter_controls()

    def _build_tab_edges(self) -> None:
        # Build the Edges tab UI.
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        form = QtWidgets.QFormLayout()
        self.edge_type = QtWidgets.QComboBox()
        self.edge_type.addItems(["Sobel", "Roberts", "Prewitt", "Canny"])
        self.edge_type.currentIndexChanged.connect(self._update_edge_controls)

        self.sobel_ksize = QtWidgets.QSpinBox()
        self.sobel_ksize.setRange(3, 9)
        self.sobel_ksize.setSingleStep(2)
        self.sobel_ksize.setValue(3)

        self.canny_low = QtWidgets.QSpinBox()
        self.canny_low.setRange(0, 255)
        self.canny_low.setValue(50)
        self.canny_high = QtWidgets.QSpinBox()
        self.canny_high.setRange(0, 255)
        self.canny_high.setValue(150)

        form.addRow("Edge type", self.edge_type)
        form.addRow("Sobel ksize", self.sobel_ksize)
        form.addRow("Canny low", self.canny_low)
        form.addRow("Canny high", self.canny_high)

        self.btn_apply_edge = QtWidgets.QPushButton("Apply Edge")
        self.btn_apply_edge.clicked.connect(self.apply_edges)

        images = QtWidgets.QHBoxLayout()
        self.panel_edge_in = ImagePanel("Input (Gray)")
        self.panel_edge_x = ImagePanel("Edge X")
        self.panel_edge_y = ImagePanel("Edge Y")
        self.panel_edge_mag = ImagePanel("Magnitude")
        images.addWidget(self.panel_edge_in)
        images.addWidget(self.panel_edge_x)
        images.addWidget(self.panel_edge_y)
        images.addWidget(self.panel_edge_mag)

        layout.addLayout(form)
        layout.addWidget(self.btn_apply_edge)
        layout.addLayout(images)
        self.tabs.addTab(widget, "Edges")
        self._update_edge_controls()

    def open_image(self) -> None:
        # Load image from disk and reset the pipeline state.
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open image", "", "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )
        if not path:
            return
        self.original_bgr = read_image_bgr(path)
        self.gray = to_gray(self.original_bgr)
        self.noisy = None
        self.filtered = None
        self.panel_original.set_image(self.original_bgr)
        self.panel_gray.set_image(self.gray)
        self.panel_noise_in.set_image(self.original_bgr)
        self.panel_filter_in.set_image(self.original_bgr)
        self.panel_edge_in.set_image(self.gray)
        self.filter_source_status.setText("Noisy image: not available")

    def save_edited(self) -> None:
        # Save the selected output image to disk.
        image = self._get_save_source()
        if image is None:
            QtWidgets.QMessageBox.information(self, "Save image", "Selected image is not available yet.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save image", "", "PNG (*.png);;JPG (*.jpg)")
        if not path:
            return
        choice = self.save_target.currentText()
        if choice.startswith("Noisy") or choice.startswith("Filtered"):
            to_save = image
        else:
            if len(image.shape) == 2:
                to_save = image
            else:
                to_save = to_gray(image)
        if not cv2.imwrite(path, to_save):
            QtWidgets.QMessageBox.warning(self, "Save image", "Failed to save image. Check the file path.")

    def _get_save_source(self) -> np.ndarray | None:
        # Resolve which image to save based on the dropdown.
        choice = self.save_target.currentText()
        if choice.startswith("Gray"):
            return self.gray
        if choice.startswith("Original"):
            return self.original_bgr
        if choice.startswith("Noisy"):
            return self.noisy
        if choice.startswith("Filtered"):
            return self.filtered
        if choice.startswith("Edges (Magnitude)"):
            return self.panel_edge_mag._image
        if choice.startswith("Edges (X)"):
            return self.panel_edge_x._image
        if choice.startswith("Edges (Y)"):
            return self.panel_edge_y._image
        return None

    def _update_noise_controls(self) -> None:
        # Enable only the parameters used by the selected noise type.
        is_uniform = self.noise_type.currentText() == "Uniform"
        is_gauss = self.noise_type.currentText() == "Gaussian"
        is_sp = self.noise_type.currentText() == "Salt & Pepper"

        self._set_control_enabled(self.uniform_low, is_uniform, "Used only for Uniform noise")
        self._set_control_enabled(self.uniform_high, is_uniform, "Used only for Uniform noise")
        self._set_control_enabled(self.gauss_mean, is_gauss, "Used only for Gaussian noise")
        self._set_control_enabled(self.gauss_sigma, is_gauss, "Used only for Gaussian noise")
        self._set_control_enabled(self.sp_amount, is_sp, "Used only for Salt & Pepper noise")
        self._set_control_enabled(self.sp_ratio, is_sp, "Used only for Salt & Pepper noise")

    def _update_filter_controls(self) -> None:
        # Enable only the parameters used by the selected filter type.
        is_gauss = self.filter_type.currentText() == "Gaussian"
        self._set_control_enabled(self.filter_sigma, is_gauss, "Used only for Gaussian filter")

    def _update_edge_controls(self) -> None:
        # Enable only the parameters used by the selected edge detector.
        is_sobel = self.edge_type.currentText() == "Sobel"
        is_canny = self.edge_type.currentText() == "Canny"
        self._set_control_enabled(self.sobel_ksize, is_sobel, "Used only for Sobel")
        self._set_control_enabled(self.canny_low, is_canny, "Used only for Canny")
        self._set_control_enabled(self.canny_high, is_canny, "Used only for Canny")

    def apply_noise(self) -> None:
        # Apply noise to the original image.
        if self.original_bgr is None:
            return
        if self.noise_type.currentText() == "Uniform":
            self.noisy = add_uniform_noise(
                self.original_bgr, self.uniform_low.value(), self.uniform_high.value()
            )
        elif self.noise_type.currentText() == "Gaussian":
            self.noisy = add_gaussian_noise(self.original_bgr, self.gauss_mean.value(), self.gauss_sigma.value())
        else:
            self.noisy = add_salt_pepper_noise(
                self.original_bgr, self.sp_amount.value(), self.sp_ratio.value()
            )
        self.panel_noisy.set_image(self.noisy)
        self.filter_source_status.setText("Noisy image: available")

    def apply_filter(self) -> None:
        # Apply the selected filter to original or noisy image.
        if self.original_bgr is None:
            return
        if self.filter_source.currentText().startswith("Noisy") and self.noisy is not None:
            source = self.noisy
        else:
            source = self.original_bgr
        ksize = self._odd_ksize(self.filter_ksize.value())
        if self.filter_type.currentText() == "Average":
            self.filtered = apply_average_filter(source, ksize)
        elif self.filter_type.currentText() == "Gaussian":
            self.filtered = apply_gaussian_filter(source, ksize, self.filter_sigma.value())
        else:
            self.filtered = apply_median_filter(source, ksize)
        self.panel_filtered.set_image(self.filtered)

    def apply_edges(self) -> None:
        # Compute edges from the current source image.
        if self.original_bgr is None:
            return
        source = self.filtered if self.filtered is not None else self.original_bgr
        gray = to_gray(source)
        self.panel_edge_in.set_image(gray)

        if self.edge_type.currentText() == "Sobel":
            gx, gy, mag = edge_sobel(gray, self.sobel_ksize.value())
            self.panel_edge_x.set_image(gx)
            self.panel_edge_y.set_image(gy)
            self.panel_edge_mag.set_image(mag)
        elif self.edge_type.currentText() == "Roberts":
            gx, gy, mag = edge_roberts(gray)
            self.panel_edge_x.set_image(gx)
            self.panel_edge_y.set_image(gy)
            self.panel_edge_mag.set_image(mag)
        elif self.edge_type.currentText() == "Prewitt":
            gx, gy, mag = edge_prewitt(gray)
            self.panel_edge_x.set_image(gx)
            self.panel_edge_y.set_image(gy)
            self.panel_edge_mag.set_image(mag)
        else:
            # Canny is OpenCV-only; preview only the final edge map.
            edges = edge_canny(gray, self.canny_low.value(), self.canny_high.value())
            self.panel_edge_x.set_image(None)
            self.panel_edge_y.set_image(None)
            self.panel_edge_mag.set_image(edges)

    @staticmethod
    def _odd_ksize(value: int) -> int:
        # Ensure kernel size is odd.
        if value % 2 == 0:
            return value + 1
        return value

    @staticmethod
    def _set_control_enabled(widget: QtWidgets.QWidget, enabled: bool, hint: str) -> None:
        # Apply enabled state and visual hint for inactive controls.
        widget.setEnabled(enabled)
        widget.setToolTip(hint)
        if enabled:
            widget.setStyleSheet("")
        else:
            widget.setStyleSheet("color:#8a8376;background:#efe9e0;")

    @staticmethod
    def _build_theme() -> str:
        # Return the app stylesheet.
        return (
            "QWidget{background:#f3efe8;color:#2b2b2b;font-size:14px;}"
            "QTabWidget::pane{border:1px solid #d0c7b8;border-radius:8px;padding:6px;background:#f9f5ef;}"
            "QTabBar::tab{background:#e7dfd0;border:1px solid #cfc5b4;border-bottom:none;"
            "padding:8px 14px;margin-right:4px;border-top-left-radius:8px;border-top-right-radius:8px;}"
            "QTabBar::tab:selected{background:#f9f5ef;color:#1e1e1e;}"
            "QGroupBox{border:1px solid #d0c7b8;border-radius:8px;margin-top:10px;padding:8px;}"
            "QPushButton{background:#2f4b5a;color:#ffffff;border:none;border-radius:8px;padding:8px 14px;}"
            "QPushButton:hover{background:#3b5e70;}"
            "QPushButton:pressed{background:#26414d;}"
            "QComboBox,QSpinBox,QDoubleSpinBox{background:#ffffff;border:1px solid #cfc5b4;border-radius:6px;padding:4px;}"
            "QLabel{color:#2b2b2b;}"
        )


def main() -> None:
    # App entry point.
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
