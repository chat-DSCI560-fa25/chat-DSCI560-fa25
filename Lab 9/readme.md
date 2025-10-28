## Docker 

This project uses Docker and Docker Compose to manage dependencies and ensure a consistent Python 3.11 environment.

**Prerequisites:**
* Docker installed
* Docker Compose installed

**Setup:**

1.  **Clone the Repository:** Get the code from GitHub.
2.  **Download the LLM:** This repository does not include the large language model file. Please download the required Llama 2 GGUF model using the link provided in `model.txt` and place the downloaded `.gguf` file inside the `models` folder in the project's root directory.
3.  **Additional PDFs:** Place the PDF documents you want to chat with inside the `pdf_files` folder.

**Execution:**

1.  **Build and Start Container:** Open a terminal in the project's root directory and run:
    ```bash
    docker-compose up -d --build
    ```
2.  **Open Shell in Container:** Once the container is running, open an interactive shell inside it:
    ```bash
    docker-compose exec lab9 bash
    ```
3.  **Run the Script:** You are now inside the container. Run the chatbot script:
    ```bash
    python3 exec_model_cli.py
    ```
    The script will process the PDFs and prompt you to ask questions.

**Stopping:**

1.  **Stop and Remove Container:** When you are finished, stop the container from your host terminal:
    ```bash
    docker-compose down
    ```
