import sys
import os
import time
import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                           QWidget, QLabel, QFileDialog, QHBoxLayout, QMessageBox,
                           QFrame, QSizePolicy, QToolTip, QStatusBar)
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QPainterPath, QPen, QColor, QBrush, QFont
from PyQt5.QtCore import Qt, QRect, QPoint, QRectF, QSize

class CaptureUI(QMainWindow):
    def __init__(self, capture_module):
        super().__init__()
        self.capture_module = capture_module
        self.is_selecting = False
        self.selection_start = QPoint()
        self.selection_end = QPoint()
        self.selection_rect = QRect()
        self.last_capture_path = None
        
        # Initialize save path before initUI method
        self.default_save_dir = os.path.join(os.path.expanduser("~"), "Pictures", "ScreenCaptures")
        
        # Create directory if it doesn't exist
        if not os.path.exists(self.default_save_dir):
            os.makedirs(self.default_save_dir)
            
        # Initialize UI
        self.initUI()

    def initUI(self):
        """Initialize UI"""
        # Basic window settings
        self.setWindowTitle('Snipix')
        self.setGeometry(100, 100, 650, 550)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 16px;
            }
            QPushButton {
                background-color: rgba(52, 73, 94, 0.8);
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(52, 73, 94, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(52, 73, 94, 1.0);
            }
            QStatusBar {
                background-color: #e0e0e0;
                font-size: 15px;
            }
        """)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Program title
        title_label = QLabel('Snipix')
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333333; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Guide message
        guide_label = QLabel('Select the capture method you want')
        guide_label.setStyleSheet("font-size: 16px; color: #555555; margin-bottom: 5px;")
        guide_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(guide_label)

        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        # Full screen capture button
        self.capture_btn = QPushButton('Full Screen Capture')
        self.capture_btn.setMinimumHeight(60)
        self.capture_btn.setToolTip('Capture the entire screen')
        self.capture_btn.setIcon(QIcon.fromTheme('camera-photo'))
        self.capture_btn.clicked.connect(self.capture_full_screen)
        btn_layout.addWidget(self.capture_btn)

        # Area capture button
        self.area_btn = QPushButton('Rectangular Area Capture')
        self.area_btn.setMinimumHeight(60)
        self.area_btn.setToolTip('Drag to select an area to capture')
        self.area_btn.setIcon(QIcon.fromTheme('select-rectangular'))
        self.area_btn.clicked.connect(self.capture_area)
        btn_layout.addWidget(self.area_btn)

        # Add button layout
        main_layout.addLayout(btn_layout)

        # Add separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #cccccc;")
        main_layout.addWidget(line)

        # Preview title
        preview_title = QLabel('Captured Image Preview')
        preview_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333;")
        preview_title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(preview_title)

        # Preview frame
        preview_frame = QFrame()
        preview_frame.setFrameShape(QFrame.StyledPanel)
        preview_frame.setFrameShadow(QFrame.Sunken)
        preview_frame.setStyleSheet("background-color: white; border: 1px solid #cccccc; border-radius: 4px;")
        preview_layout = QVBoxLayout(preview_frame)

        # Preview label
        self.preview_label = QLabel('The preview will be displayed here after capture')
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("color: #888888; font-size: 16px;")
        self.preview_label.setMinimumHeight(280)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_layout.addWidget(self.preview_label)

        # Add preview frame
        main_layout.addWidget(preview_frame)

        # Save button layout
        save_layout = QHBoxLayout()
        save_layout.setSpacing(15)
        
        # Save path display label
        self.path_label = QLabel(f'Save Path: {self.default_save_dir}')
        self.path_label.setStyleSheet("font-size: 15px; color: #555555;")
        save_layout.addWidget(self.path_label)
        
        # Set save path button
        self.path_btn = QPushButton('Change Path')
        self.path_btn.setMinimumHeight(45)
        self.path_btn.setMinimumWidth(150)
        self.path_btn.setToolTip('Change the save location for captured images')
        self.path_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(241, 196, 15, 0.8);
                font-size: 15px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(241, 196, 15, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(241, 196, 15, 1.0);
            }
        """)
        self.path_btn.clicked.connect(self.set_save_path)
        save_layout.addWidget(self.path_btn)
        
        # Add spacer (for right alignment)
        save_layout.addStretch()
        
        # Save button
        self.save_btn = QPushButton('Save')
        self.save_btn.setMinimumHeight(45)
        self.save_btn.setMinimumWidth(140)
        self.save_btn.setToolTip('Save the captured image')
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(231, 76, 60, 0.8);
                font-size: 17px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(231, 76, 60, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(231, 76, 60, 1.0);
            }
        """)
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        save_layout.addWidget(self.save_btn)
        
        # Add save button layout
        main_layout.addLayout(save_layout)

        # Status bar setup
        status_bar = QStatusBar()
        status_bar.setStyleSheet("padding: 7px; font-size: 15px;")
        self.setStatusBar(status_bar)
        self.statusBar().showMessage('Ready')

        # Tooltip font setup
        QToolTip.setFont(QFont('Arial', 14))

    def capture_full_screen(self):
        """Perform full screen capture"""
        self.statusBar().showMessage('Capturing full screen...')
        self.hide()  # Hide window during capture
        
        # Apply slight delay (time for window to completely disappear)
        QApplication.processEvents()
        time.sleep(0.2)  # Short delay
        
        # Perform capture
        self.last_capture_path = self.capture_module.capture_full_screen()
        
        # Update preview
        self.update_preview(self.last_capture_path)
        
        # Restore UI
        self.show()
        self.statusBar().showMessage('Full screen capture completed - Press Save button to save the image')
        self.save_btn.setEnabled(True)

    def capture_area(self):
        """Start area selection capture mode"""
        self.statusBar().showMessage('Rectangular area selection mode - Drag to select an area')
        
        # Create and display separate area selection window
        self.area_selector = AreaSelector(self)
        self.hide()  # Hide main window
        
        # Apply slight delay (time for window to completely disappear)
        QApplication.processEvents()
        time.sleep(0.2)  # Short delay
        
        # Display area selector
        self.area_selector.show()
        self.area_selector.activateWindow()
        self.area_selector.raise_()

    def process_area_selection(self, rect):
        """Process area selection"""
        if rect.width() > 0 and rect.height() > 0:
            # Perform capture with selected area
            self.last_capture_path = self.capture_module.capture_area(
                rect.x(), rect.y(), rect.width(), rect.height())
            
            # Update preview
            self.update_preview(self.last_capture_path)
            self.statusBar().showMessage('Area capture completed - Press Save button to save the image')
            self.save_btn.setEnabled(True)
        else:
            self.statusBar().showMessage('Area selection canceled.')

    def update_preview(self, image_path):
        """Update captured image preview"""
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            # Scale image to fit label
            scaled_pixmap = pixmap.scaled(
                self.preview_label.width(), 
                self.preview_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
            self.preview_label.setStyleSheet("")  # Reset style
        else:
            self.preview_label.setText('Cannot load image')
            self.preview_label.setStyleSheet("color: #888888; font-size: 16px;")

    def set_save_path(self):
        """Set save path"""
        dir_path = QFileDialog.getExistingDirectory(
            self, 'Select Save Location', 
            self.default_save_dir,
            QFileDialog.ShowDirsOnly
        )
        
        if dir_path:
            self.default_save_dir = dir_path
            self.path_label.setText(f'Save Path: {self.default_save_dir}')
            self.statusBar().showMessage(f'Save path has been changed')

    def save_image(self):
        """Save captured image"""
        if not self.last_capture_path or not os.path.exists(self.last_capture_path):
            QMessageBox.warning(self, "Save Error", "No captured image to save.")
            return
        
        # Auto-generate filename (based on current date and time)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        
        # Create save path
        file_path = os.path.join(self.default_save_dir, filename)
        
        try:
            # Copy file
            import shutil
            shutil.copy2(self.last_capture_path, file_path)
            self.statusBar().showMessage(f'Image has been saved')
            
            # Display success message
            QMessageBox.information(self, "Save Complete", f"Image has been successfully saved.\n\nFile path: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"An error occurred while saving the file: {str(e)}")

    def resizeEvent(self, event):
        """Update preview when window size changes"""
        if hasattr(self, 'last_capture_path') and self.last_capture_path and os.path.exists(self.last_capture_path):
            self.update_preview(self.last_capture_path)
        super().resizeEvent(event)


class AreaSelector(QWidget):
    """Widget for selecting screen area"""
    def __init__(self, parent=None):
        super().__init__(None)  # Create as top-level window without parent
        self.parent = parent
        self.initUI()
        self.selection_start = QPoint()
        self.selection_end = QPoint()
        self.is_selecting = False

    def initUI(self):
        """Initialize UI"""
        # Set window to full screen size
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(QApplication.primaryScreen().geometry())
        
        # Set transparent background
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 50);")
        
        # Set cursor
        self.setCursor(Qt.CrossCursor)
        
        # Help label
        self.help_label = QLabel("Drag to select rectangular area, ESC to cancel", self)
        self.help_label.setStyleSheet("""
            color: white; 
            background-color: rgba(0, 0, 0, 180); 
            padding: 12px; 
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
        """)
        self.help_label.move(20, 20)
        self.help_label.adjustSize()

    def paintEvent(self, event):
        """Paint event for displaying selection area"""
        painter = QPainter(self)
        
        # Draw semi-transparent overlay over entire screen
        painter.fillRect(self.rect(), QColor(0, 0, 0, 50))
        
        # If area is being selected, make that area transparent
        if self.is_selecting and not self.selection_start.isNull():
            selection_rect = QRect(self.selection_start, self.selection_end)
            selection_rect = selection_rect.normalized()
            
            # QRectF conversion (use QRectF instead of QRect)
            selection_rectf = QRectF(selection_rect)
            
            # Make selection area transparent
            mask = QPainterPath()
            mask.addRect(QRectF(self.rect()))
            inner = QPainterPath()
            inner.addRect(selection_rectf)
            mask = mask.subtracted(inner)
            painter.fillPath(mask, QColor(0, 0, 0, 100))
            
            # Make selected area more transparent
            painter.fillRect(selection_rect, QColor(255, 255, 255, 10))
            
            # Draw selection area border (thicker and more visible color)
            pen = QPen(QColor(0, 200, 255), 3)
            pen.setStyle(Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(selection_rect)
            
            # Display selection area size
            size_text = f"{selection_rect.width()} x {selection_rect.height()}"
            size_bg_rect = QRect(selection_rect.bottomRight().x() - 150, 
                                selection_rect.bottomRight().y() + 10, 150, 30)
            
            # Size display background
            painter.fillRect(size_bg_rect, QColor(0, 0, 0, 180))
            
            # Size text drawing
            painter.setPen(QColor(255, 255, 255))
            font = painter.font()
            font.setPointSize(12)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(size_bg_rect, Qt.AlignCenter, size_text)
            
            # Corner markers
            corner_size = 10
            corner_color = QColor(0, 200, 255)
            painter.setBrush(QBrush(corner_color))
            painter.setPen(Qt.NoPen)
            
            # Top-left
            painter.drawRect(QRect(selection_rect.left() - corner_size//2, 
                                selection_rect.top() - corner_size//2, 
                                corner_size, corner_size))
            # Top-right
            painter.drawRect(QRect(selection_rect.right() - corner_size//2, 
                                selection_rect.top() - corner_size//2, 
                                corner_size, corner_size))
            # Bottom-left
            painter.drawRect(QRect(selection_rect.left() - corner_size//2, 
                                selection_rect.bottom() - corner_size//2, 
                                corner_size, corner_size))
            # Bottom-right
            painter.drawRect(QRect(selection_rect.right() - corner_size//2, 
                                selection_rect.bottom() - corner_size//2, 
                                corner_size, corner_size))

    def mousePressEvent(self, event):
        """Mouse button press event"""
        if event.button() == Qt.LeftButton:
            self.selection_start = event.pos()
            self.selection_end = self.selection_start
            self.is_selecting = True

    def mouseMoveEvent(self, event):
        """Mouse movement event"""
        if self.is_selecting:
            self.selection_end = event.pos()
            self.update()  # Refresh display

    def mouseReleaseEvent(self, event):
        """Mouse button release event"""
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.selection_end = event.pos()
            self.is_selecting = False
            
            # Calculate selection area
            selection_rect = QRect(self.selection_start, self.selection_end).normalized()
            
            # Close window after selection is complete
            self.close()
            
            # Pass selection information to parent
            if self.parent:
                self.parent.show()  # Show main window again
                self.parent.process_area_selection(selection_rect)

    def keyPressEvent(self, event):
        """Key event handling"""
        # Cancel with ESC key
        if event.key() == Qt.Key_Escape:
            self.close()
            if self.parent:
                self.parent.show()
                self.parent.statusBar().showMessage('Rectangular area selection canceled.') 