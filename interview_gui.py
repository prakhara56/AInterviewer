import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit, QLineEdit, QWidget, QMessageBox, QTabWidget, QStatusBar
)
import requests

API_URL = "http://localhost:8000"  # Your FastAPI backend URL


class AIInterviewAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Interview Assistant")
        self.setGeometry(100, 100, 900, 600)

        # Central Widget and Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Tab Widget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Tabs
        self.create_upload_tab()
        self.create_guidelines_tab()
        self.create_chat_tab()
        self.create_feedback_tab()

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def create_upload_tab(self):
        """Tab for uploading job descriptions."""
        self.upload_tab = QWidget()
        self.tab_widget.addTab(self.upload_tab, "Upload Job Description")

        layout = QVBoxLayout(self.upload_tab)

        self.upload_label = QLabel("Upload a Job Description PDF:")
        layout.addWidget(self.upload_label)

        self.upload_button = QPushButton("Upload PDF")
        self.upload_button.clicked.connect(self.upload_pdf)
        layout.addWidget(self.upload_button)

        self.upload_status = QLabel("")
        layout.addWidget(self.upload_status)

    def create_guidelines_tab(self):
        """Tab for displaying generated interview guidelines."""
        self.guidelines_tab = QWidget()
        self.tab_widget.addTab(self.guidelines_tab, "View Guidelines")

        layout = QVBoxLayout(self.guidelines_tab)

        self.guidelines_text = QTextEdit()
        self.guidelines_text.setReadOnly(True)
        layout.addWidget(self.guidelines_text)

        self.refresh_guidelines_button = QPushButton("Refresh Guidelines")
        self.refresh_guidelines_button.clicked.connect(self.refresh_guidelines)
        layout.addWidget(self.refresh_guidelines_button)

    def create_chat_tab(self):
        """Tab for interacting with the AI."""
        self.chat_tab = QWidget()
        self.tab_widget.addTab(self.chat_tab, "Chat with AI")

        layout = QVBoxLayout(self.chat_tab)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(self.chat_history)

        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message here...")
        input_layout.addWidget(self.chat_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

    def create_feedback_tab(self):
        """Tab for requesting feedback."""
        self.feedback_tab = QWidget()
        self.tab_widget.addTab(self.feedback_tab, "Request Feedback")

        layout = QVBoxLayout(self.feedback_tab)

        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)
        layout.addWidget(self.feedback_text)

        self.generate_feedback_button = QPushButton("Generate Feedback")
        self.generate_feedback_button.clicked.connect(self.generate_feedback)
        layout.addWidget(self.generate_feedback_button)

    def upload_pdf(self):
        """Upload a PDF to the backend."""
        file_path = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")[0]
        if not file_path:
            return

        self.status_bar.showMessage("Uploading PDF...")
        try:
            with open(file_path, "rb") as file:
                response = requests.post(f"{API_URL}/upload_job_description/", files={"file": file})
            if response.status_code == 200:
                self.upload_status.setText("PDF uploaded successfully!")
                self.status_bar.showMessage("PDF uploaded successfully.", 5000)
            else:
                raise Exception(response.json().get("detail", "Unknown error"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to upload PDF: {e}")
            self.status_bar.showMessage("Upload failed.", 5000)

    def refresh_guidelines(self):
        """Fetch guidelines from the backend."""
        self.status_bar.showMessage("Fetching guidelines...")
        try:
            response = requests.get(f"{API_URL}/get_guidelines/")
            if response.status_code == 200:
                guidelines = response.json().get("guidelines", "No guidelines found.")
                self.guidelines_text.setPlainText(guidelines)
                self.status_bar.showMessage("Guidelines fetched successfully.", 5000)
            else:
                raise Exception(response.json().get("detail", "Unknown error"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch guidelines: {e}")
            self.status_bar.showMessage("Failed to fetch guidelines.", 5000)

    def send_message(self):
        """Send a message to the backend and get a response."""
        user_input = self.chat_input.text().strip()
        if not user_input:
            return

        self.chat_history.append(f"User: {user_input}")
        self.chat_input.clear()
        self.status_bar.showMessage("Sending message...")
        try:
            response = requests.post(f"{API_URL}/ask_question/", json={"user_input": user_input})
            if response.status_code == 200:
                ai_response = response.json().get("response", "No response.")
                self.chat_history.append(f"AI: {ai_response}")
                self.status_bar.showMessage("Response received.", 5000)
            else:
                raise Exception(response.json().get("detail", "Unknown error"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get AI response: {e}")
            self.status_bar.showMessage("Failed to get AI response.", 5000)

    def generate_feedback(self):
        """Request feedback from the backend."""
        self.status_bar.showMessage("Generating feedback...")
        try:
            response = requests.get(f"{API_URL}/generate_feedback/")
            if response.status_code == 200:
                feedback = response.json().get("feedback", "No feedback generated.")
                self.feedback_text.setPlainText(feedback)
                self.status_bar.showMessage("Feedback generated successfully.", 5000)
            else:
                raise Exception(response.json().get("detail", "Unknown error"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate feedback: {e}")
            self.status_bar.showMessage("Failed to generate feedback.", 5000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AIInterviewAssistant()
    window.show()
    sys.exit(app.exec_())