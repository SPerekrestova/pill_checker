# **Meds Recognition**

## Overview

MedsRecognition is a Django-based application designed to recognize medications from scanned images. The recognition workflow consists of extracting text via OCR, then leveraging a remote biomedical Named Entity Recognition (NER) service to identify active ingredients within the extracted text.

> **⚠️ Note**: This project is a work in progress, created for educational purposes to explore new technology stacks and AI/ML possibilities. Some features may not be fully implemented or finalized.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Installing and Running Locally](#installing-and-running-locally)
- [Docker Usage](#docker-usage)
- [Contributing](#contributing)
- [License](#license)

## Features

### 1. **OCR for Medication Recognition**  
- Converts uploaded images into text.
- Passes extracted text to a remote biomedical service for active ingredient detection.

### 2. **Biomed Service Integration**  
- Connects to an external NER API for processing recognized text.  
- For more information on the NER service, refer to:  
  [BiomedNER GitHub Repository](https://github.com/SPerekrestova/BiomedNER).

### 3. **Authentication and Profile Management**  
- Provides user sign-up and sign-in via Supabase integration.  
- Stores user profiles within the Django application.

### 4. **API Endpoints**  
- Includes endpoints suitable for mobile or web clients to interact with user and medication data.  
- Allows scanning (via OCR) and subsequent recognition of medication ingredients.

### 5. **Docker Support**  
- A Dockerfile is provided for containerizing and deploying the application.

## Project Structure

The project consists of the following key components:

### **biomed_ner_client.py**
- Contains a client class to call the remote BiomedNER API.
- Sends scanned text to the external service and processes the returned list of recognized entities.
- Uses environment variables for configuration:
  - `BIOMED_HOST` (required)
  - `BIOMED_SCHEME` (optional, defaults to `http`)

### **ocr_service.py**
- Integrates the external BiomedNER client after performing OCR.
- Submits extracted text to the BiomedNER service and retrieves recognized ingredients.

---

## Prerequisites

- Python 3  
- Docker (optional for containerization)  

## Environment Variables

The application relies on the following environment variables:

- `BIOMED_HOST` – Host address for the BiomedNER service.  
- `BIOMED_SCHEME` – Optional scheme (http/https) for the BiomedNER service.  

Additional Supabase or project-related variables can be configured for authentication and other features.

## Installing and Running Locally

1. **Clone the Repository**  
   Obtain the source files and navigate into the project directory.

2. **Setup a Virtual Environment (Recommended)**  
   Install any standard Python environment management tool and activate it.

3. **Install Dependencies**  
```shell script
pip install -r requirements.txt
```

4. **Configure Environment Variables**  
   Make sure to set the BiomedNER service details (BIOMED_HOST and BIOMED_SCHEME).

5. **Run Migrations**  
```shell script
python manage.py migrate
```

6. **Start the Django Development Server**  
```shell script
python manage.py runserver
```
   Access the interface or endpoints at: http://127.0.0.1:8000.

## Docker Usage

To build and run the Docker image:

1. **Build the Image**  
```shell script
docker build -t medsrecognition .
```

2. **Run the Container**  
```shell script
docker run -p 8000:8000 medsrecognition
```
   The application will be available at: http://localhost:8000

---

## **License**  

This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for details.  

---

## **Contact**  

**Author**: Svetlana Perekrestova  
**Email**: [svetlana.perekrestova2@gmail.com](mailto:svetlana.perekrestova2@gmail.com)  

Feel free to reach out with questions, suggestions, or feedback!  
