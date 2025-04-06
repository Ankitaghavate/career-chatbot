from flask import Flask, request, render_template, session, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use a valid model name (replace 'chat-bison-001' with the correct model name if needed)
MODEL_NAME = "gemini-1.5-pro"


class ChatSession:
    def __init__(self, history=None):
        self.history = history or []

    def add_message(self, role, content):
        """Add a message to the chat history with proper role validation."""
        if role not in ["user", "model"]:  # Ensure valid roles
            raise ValueError("Invalid role. Allowed roles are 'user' and 'model'.")
        self.history.append({"role": role, "parts": [content]})

    def to_dict(self):
        """Convert ChatSession object to a dictionary."""
        return {"history": self.history}

    @classmethod
    def from_dict(cls, data):
        """Create a ChatSession object from a dictionary."""
        return cls(history=data.get("history", []))


@app.route("/", methods=["GET", "POST"])
def chat():
    if "chat" not in session:
        # Initialize chat session and store in session
        session["chat"] = ChatSession().to_dict()

    # Retrieve chat session from session
    chat_session = ChatSession.from_dict(session["chat"])

    if request.method == "POST":
        user_input = request.form["message"]

        try:
            # Add user message to history
            chat_session.add_message("user", user_input)

            # Send message to Gemini API using valid model name
            response = genai.GenerativeModel(MODEL_NAME).start_chat(
                history=chat_session.history
            ).send_message(user_input)

            # Add bot response to history
            chat_session.add_message("model", response.text)

            # Save updated chat session back into session
            session["chat"] = chat_session.to_dict()

            return jsonify({"response": response.text})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return render_template("chat.htm")


@app.route("/report")
def report():
    """Generate and display the report."""
    chat_session = ChatSession.from_dict(session.get("chat", {}))

    # Example report data (replace with actual logic)
    report_data = {
        "summary": "Career guidance report based on your inputs.",
        "swot_analysis": {
            "strengths": ["Good communication", "Analytical thinking"],
            "weaknesses": ["Time management"],
            "opportunities": ["Growing demand in tech"],
            "threats": ["Economic instability"],
        },
        "career_options": [
            {
                "title": "Data Scientist",
                "description": "Analyze data to extract insights.",
                "growth_projections": "High",
                "salary_range": "$80k-$120k",
            },
            {
                "title": "Software Engineer",
                "description": "Develop and maintain software.",
                "growth_projections": "Moderate",
                "salary_range": "$70k-$110k",
            },
        ],
    }

    return render_template("report.htm", report=report_data)


if __name__ == "__main__":
    app.run(debug=True)
