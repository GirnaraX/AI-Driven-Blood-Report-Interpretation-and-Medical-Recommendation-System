import google.generativeai as genai
import streamlit as st
import os
from dotenv import load_dotenv


# Load environment variables from .env file (if exists)
load_dotenv()

class BloodReportChat:
    def __init__(self):
        """Initialize the chat assistant with Google Gemini API key from environment."""
        self.model = None
        self.context = None
        api_key = None
        try:
            # Try to get API key from st.secrets (Streamlit Cloud) or environment variable
            if hasattr(st, "secrets") and "gemini" in st.secrets:
                api_key = st.secrets["gemini"]["api_key"]
            else:
                api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                # No API key found, leave model as None
                return
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            # Any error during initialization, just leave model as None
            pass

    def set_context(self, patient_info, report_data, analysis_results):
        """Store the blood report analysis as context."""
        self.context = {
            "patient_info": patient_info,
            "report_data": report_data,
            "analysis_results": analysis_results
        }

    def _format_context(self):
        """Format the stored context into a readable text for the AI."""
        if not self.context:
            return "No blood report data available."

        patient = self.context["patient_info"]
        results = self.context["analysis_results"]

        context_str = f"Patient: {patient.get('name', 'Unknown')}, {patient.get('age', '?')} years, {patient.get('gender', 'unknown')}\n"
        context_str += f"Report date: {patient.get('report_date', 'unknown')}\n"
        context_str += f"Blood group: {patient.get('blood_group', 'unknown')}\n\n"

        context_str += "Analysis Summary:\n"
        context_str += results.get("summary", "No summary available.") + "\n\n"

        abnormal = results.get("abnormal_parameters", [])
        if abnormal:
            context_str += "Abnormal Parameters:\n"
            for p in abnormal:
                context_str += f"- {p['parameter']}: {p['value']} {p['unit']} (normal: {p['low']}-{p['high']}) - {p['status'].upper()}\n"
        else:
            context_str += "No abnormal parameters found.\n"

        critical = results.get("critical_parameters", [])
        if critical:
            context_str += "\nCritical Parameters (requires immediate attention):\n"
            for p in critical:
                context_str += f"- {p['parameter']}: {p['value']} {p['unit']} (normal: {p['low']}-{p['high']})\n"

        conditions = results.get("conditions_detected", [])
        if conditions:
            context_str += "\nPotential Conditions Detected:\n"
            for c in conditions:
                context_str += f"- {c['condition']} (severity: {c['severity']})\n"

        recs = results.get("recommendations", [])
        if recs:
            context_str += "\nRecommendations:\n"
            for r in recs:
                context_str += f"- For {r['condition']}: {', '.join(r['recommendations'])}. Follow-up: {r['follow_up']}\n"

        return context_str

    def get_response(self, user_message, conversation_history=None):
        """Send the user message along with the context to the Gemini AI."""
        if not self.model:
            return "🤖 Gemini AI is not available. Please set the GEMINI_API_KEY environment variable or add it to Streamlit secrets."
        if not self.context:
            return "Please analyze a blood report first. The AI needs the report data to answer your questions."

        # Build system prompt
        system_prompt = (
            "You are a helpful medical assistant specialized in interpreting blood test reports. "
            "You have access to the patient's blood report data and the analysis results. "
            "Provide clear, concise, and educational answers. If you are unsure, advise consulting a doctor. "
            "Do not give medical advice that could replace a professional diagnosis.\n\n"
            f"Here is the blood report context:\n{self._format_context()}"
        )

        # Prepare conversation history for Gemini
        messages = []
        if conversation_history:
            for msg in conversation_history:
                if msg["role"] != "system":
                    messages.append(msg)

        # Build the prompt for Gemini (concatenated text)
        prompt = ""
        if not messages:
            prompt = f"{system_prompt}\n\nUser: {user_message}\nAssistant:"
        else:
            for msg in messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                prompt += f"{role}: {msg['content']}\n"
            prompt += f"User: {user_message}\nAssistant:"

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error contacting Gemini: {str(e)}"