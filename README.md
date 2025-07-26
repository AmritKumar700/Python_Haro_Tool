-----

````markdown
# HARO Answer's Automation Tool (Multi-Variant)

![DWS Logo](https://media.glassdoor.com/sqll/868966/digital-web-solutions-squarelogo-1579870425403.png)

This is a powerful, AI-driven web application designed to automate the generation of highly humanized, distinct, and journalist-ready responses to HARO (Help A Reporter Out) queries. It leverages a multi-stage AI pipeline to produce 5 unique variants for each query, tailored to specific client needs.

## ✨ Key Features

* **Multi-Stage AI Pipeline:** Orchestrates advanced Large Language Models (Claude AI for drafting, OpenAI for polishing) for high-quality content generation.
* **5 Unique Variants per Query:** Generates five (5) entirely distinct, humanized, and insightful answers for each HARO query to maximize journalist pick-up rates.
* **Contextual Generation:** Tailors responses based on specific client information and guidelines provided by the user.
* **Aggressive Humanization:** Employs advanced prompt engineering to ensure answers are conversational, relatable, jargon-free, and sound genuinely human-written, including a focus on incorporating brief anecdotes or "moments."
* **Dynamic Uniqueness Constraints:** Ensures zero overlap in core ideas or phrasing between variants for the same query.
* **Intuitive Web Interface:** Built with Streamlit for easy input of queries and client information.
* **Flexible Output:** Displays results directly in the app and allows downloading of generated responses in TXT, CSV, and DOCX formats.
* **Secure Access:** Implements a simple username/password authentication layer for controlled access.

## ⚙️ How It Works (AI Pipeline)

The tool processes each HARO query through a sophisticated two-stage AI pipeline:

1.  **Angle Generation (OpenAI):** For each HARO query, OpenAI first generates 5 completely unique and distinct angles or perspectives from which an expert could answer. This ensures foundational uniqueness for each variant.
2.  **Drafting (Claude AI):** For each unique angle, Claude AI drafts a 2-paragraph response. Claude is strictly instructed to produce humanized, casual, emotionally intelligent content, incorporate a brief anecdote/story, and adhere to precise formatting (word/sentence counts) and negative constraints (fixed and dynamic based on previously generated variants).
3.  **Polishing (OpenAI):** OpenAI then takes Claude's draft and performs a final polish. Its primary task is to drastically reduce complexity and eliminate all jargon (by 15-20%), ensuring the language is natural, conversational, and highly relatable, while preserving the core message and narrative. It also enforces all distinctness and negative constraints.

## 🚀 Getting Started (Local Setup)

Follow these steps to set up and run the HARO Automation Tool on your local machine.

### Prerequisites

* **Python 3.9+:** Ensure you have Python installed.
* **Git:** Install Git (usually comes with Xcode Command Line Tools on macOS: `xcode-select --install`).
* **VS Code (Recommended IDE):** [Download Visual Studio Code](https://code.visualstudio.com/download)

### 1. Clone the Repository

Open your terminal (or VS Code's integrated terminal) and clone the project:

```bash
git clone [https://github.com/AmritKumar700/Python_Haro_Tool.git](https://github.com/AmritKumar700/Python_Haro_Tool.git)
cd Python_Haro_Tool
````

### 2\. Set Up a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3\. Install Dependencies

Install all required Python libraries:

```bash
pip install -r requirements.txt
# If requirements.txt is empty or missing, run:
# pip install streamlit openai anthropic httpx tenacity pandas python-docx python-dotenv aiohttp
# Then, generate requirements.txt:
# pip freeze > requirements.txt
```

### 4\. Configure API Keys (Local)

Your tool uses OpenAI and Anthropic API keys. For local development, store them securely:

  * Create a file named `.env` in your project's root directory (`Python_Haro_Tool/.env`).

  * Add your API keys to this file:

    ```
    # .env
    ANTHROPIC_API_KEY="sk-ant-YOUR_ANTHROPIC_API_KEY_HERE"
    OPENAI_API_KEY="sk-proj-YOUR_OPENAI_API_KEY_HERE"
    ```

    **Replace the placeholder values with your actual API keys.**

  * **Security Note:** `.env` is already listed in `.gitignore` to prevent accidental commits to your repository.

### 5\. Run the Application Locally

With your virtual environment activated, run the Streamlit app:

```bash
streamlit run src/main.py
```

Your default web browser should open to `http://localhost:8501`, displaying the HARO Automation Tool.

## 🤝 How to Use the App

The tool is designed for ease of use:

1.  **Access the App:**
      * If running locally, open `http://localhost:8501`.
      * If deployed on Streamlit Community Cloud, navigate to its public URL.
2.  **Login:**
      * The app requires authentication. Use the username and password configured in your Streamlit Cloud secrets (see Deployment section below). For local testing, ensure your `APP_CREDENTIALS` secret is configured locally in `.streamlit/secrets.toml` or that your `.env` is read correctly.
3.  **Input Queries & Client Info:**
      * You will see 4 pairs of input boxes for "HARO Query" and "Client Name & Specific Guidelines".
      * **HARO Query:** Copy and paste the full HARO query from the journalist into these boxes (one query per box).
      * **Client Name & Specific Guidelines:** For each query, provide the client's name on the *first line*, followed by any specific instructions or style guidelines for that client on subsequent lines.
          * **Example Input:**
            ```
            Digital Web Solutions
            Instructions:
            Each answer must be a maximum of 2 paragraphs or 200 words.
            Use a unique perspective that hasn’t been shared before.
            Keep it expert-level yet simple enough for a general audience.
            Only include one jargon term—avoid overcomplicating the response.
            ... (and so on)
            ```
4.  **General Guidelines (Sidebar):** Use the sidebar input box to provide overarching tone/style instructions that apply to all generated answers.
5.  **Start Automation:** Click the "Start HARO Automation" button. The app will show progress and status messages.
6.  **Review Results:** Once complete, the "Generated HARO Responses" section will appear. Each query will have an expandable section containing its 5 distinct variants. You can expand "Show Full Query & Client Guidelines" and "Debug Info" (if enabled) for more detail.
7.  **Download Results:** Download all generated answers in TXT, CSV, or DOCX formats for easy sharing and review.

## ☁️ Deployment (Streamlit Community Cloud)

This tool is designed for easy deployment on [Streamlit Community Cloud](https://share.streamlit.io/).

1.  **GitHub Repository:** Ensure your project code is pushed to a **public** GitHub repository (e.g., `AmritKumar700/Python_Haro_Tool`).
2.  **`requirements.txt`:** Ensure this file accurately lists all Python dependencies (`pip freeze > requirements.txt`).
3.  **Secure Secrets:**
      * Log in to Streamlit Community Cloud.
      * Go to your app's "Settings" -\> "Secrets".
      * Add your API keys and app credentials securely:
        ```toml
        ANTHROPIC_API_KEY = "sk-ant-YOUR_ANTHROPIC_API_KEY"
        OPENAI_API_KEY = "sk-proj-YOUR_OPENAI_API_KEY"
        APP_CREDENTIALS = '{"your_username": "your_secure_password", "another_user": "another_secure_password"}'
        ```
        (Remember to replace placeholders with your actual keys/passwords.)
4.  **Deploy:** Link your GitHub repository, specify `src/main.py` as the main file, and click "Deploy\!".

## ❓ Troubleshooting Tips

  * **`ModuleNotFoundError`:**
      * **Local:** Ensure your virtual environment is active and all dependencies in `requirements.txt` are installed (`pip install -r requirements.txt`).
      * **Cloud:** Make sure `requirements.txt` includes *all* necessary libraries (including `python-dotenv`, `aiohttp`) and is pushed to GitHub.
  * **`Invalid username or password`:** Double-check that the `APP_CREDENTIALS` secret on Streamlit Cloud is correctly formatted as JSON (`'{"username": "password"}'`) and that the entered credentials match exactly (case-sensitive).
  * **AI API Errors (e.g., `400 Bad Request`, `Credit balance too low`):**
      * **API Key:** Verify your API keys in Streamlit Cloud secrets are correct and active.
      * **Credits/Billing:** Check your OpenAI and Anthropic dashboards for credit balance, usage limits, or billing issues.
      * **Model Name:** Ensure the model names in `src/config.py` are current and permitted for your API tier (e.g., `claude-3-5-sonnet-20240620`, `gpt-4o-2024-08-06`).
  * **`StreamlitDuplicateElementId`:** This means a widget has the same `key` or implicitly got a duplicate ID. Ensure unique `key` attributes for widgets in loops or conditional blocks if needed. (This has been addressed in `main.py`).
  * **Git Push Issues (`Repository not found`, `Push declined due to repository rule violations`):**
      * **`Repository not found`:** Ensure the GitHub repository exists and the URL is correct.
      * **`Push declined due to repository rule violations`:** This means sensitive files (like API keys) were in your commit history. You need to use `git filter-repo --path .streamlit/secrets.toml --invert-paths --force` (and `git push --force origin main`) on your local repository to remove them from history. **Use this command with extreme caution.**

-----
