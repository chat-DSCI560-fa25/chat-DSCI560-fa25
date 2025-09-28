# Reddit Post Clustering and Analysis Pipeline

## Prerequisites
docker

## Setup and Installation

Follow these steps to get the project running.

1.  **Clone the Repository**

2.  **Create the Environment File**
    The project requires an environment file for secret credentials. A template is provided. Copy the template to create your own configuration file.(Accidentally did add my env,but git gurdain removed it!Pretty Cool!)

3.  **Configure Your Credentials**
    Open the newly created `.env` file with a text editor. Your personal Reddit API credentials:
    * `REDDIT_CLIENT_ID`
    * `REDDIT_CLIENT_SECRET`
    * `REDDIT_USER_AGENT`

## How to Run

1.  **Build and Start All Services**
    This single command will build the Docker images and start the Flask app, the background worker, the database, and the database GUI.
    
    sudo docker compose up -d --build
    
    Important:The background worker will automatically start scraping and processing data.
    Access the running logs for background script using
    sudo docker compose logs worker

2.  **Access the Web App**
    UI is available at:
    * **`http://localhost:5000`**

3.  You can view the raw data using phpMyAdmin at:
    * **`http://localhost:8080`**

## Usage

### Web Dashboard
The web interface at `http://localhost:5000` is for finding clusters. Enter a keyword or sentence and submit the form to see which topic your query best matches. The results are based on the latest data collected by the background worker.

### Command-Line Tools (Manual Operations)

You can run manual, one-off tasks using `docker-compose exec`. This is useful for bulk-loading data, debugging, or generating reports on demand.

**Scrape a large number of posts:**
    
    sudo docker compose exec app python main.py --scrape --limit 1000
    

**Run only the preprocessor:**
    sudo docker compose exec app python main.py --preprocess
    

**Run a full analysis and generate new visualizations:**
    docker-compose exec app python main.py --analyze
    

**Get a detailed interpretation report in your terminal:**
    sudo docker compose exec app python main.py --interpret
