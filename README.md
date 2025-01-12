
# **MedsRecognition**  
*MedsRecognition* is a Django-based application designed to extract text from uploaded images using EasyOCR and identify active ingredients in medications by querying public APIs such as **RxNav** and **OpenFDA**. The application also integrates with **Supabase** for efficient data storage and management.

> **⚠️ Note**: This project is a work in progress. Some features may not yet be fully implemented or finalized.

---

## **Table of Contents**  
1. [Features](#features)  
2. [Prerequisites](#prerequisites)  
3. [Installation](#installation)  
4. [How It Works](#how-it-works)  
5. [APIs and Integrations](#apis-and-integrations)  
6. [Usage](#usage)  
7. [License](#license)  
8. [Contact](#contact)  

---

## **Features**  
- Upload images to extract text seamlessly.  
- Supports multiple image formats (e.g., JPEG, PNG).  
- Utilizes **EasyOCR** for highly accurate text recognition.  
- Matches recognized text with active ingredients using **RxNav** and **OpenFDA APIs**.  
- Integrates with **Supabase** for centralized storage and data management.  

---

## **Prerequisites**  
- Python 3.8+  
- Pip (Python package manager)  
- Supabase account and project configuration  

---

## **Installation**  

1. **Clone the Repository**:  
   ```bash
   git clone https://github.com/SPerekrestova/MedsRecognition.git
   cd MedsRecognition
   ```

2. **Install Dependencies**:  
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Supabase**:  
   - Create a **Supabase** project [here](https://supabase.com).  
   - Note your **API key** and **project URL** from the Supabase dashboard.  
   - Add these values to your `.env` file:  
     ```env
     SUPABASE_URL=<your-supabase-url>
     SUPABASE_API_KEY=<your-supabase-api-key>
     ```

4. **Apply Migrations** *(if applicable)*:  
   ```bash
   python manage.py migrate
   ```

5. **Run the Django Server**:  
   ```bash
   python manage.py runserver
   ```

---

## **How It Works**  

### 1. **Upload Image**  
- Users upload images containing text via the web interface. Supported formats include JPEG, PNG, and more.  

### 2. **Text Recognition**  
- The uploaded image is processed using **EasyOCR**, which extracts text with support for multiple languages.  

### 3. **Database Matching**  
- Extracted text is matched against a list of active ingredients fetched in real-time using the **RxNav API** and **OpenFDA API**.  

### 4. **Supabase Integration**  
- Recognized text, extracted active ingredients, and associated metadata are securely stored in a **Supabase** database.  
- This allows for centralized data management and retrieval for analytics or future use.  

### 5. **Results Display**  
- Matched active ingredients are displayed in a user-friendly interface, allowing for easy review and further use.  

---

## **APIs and Integrations**  

### **1. Public APIs Queried**:  
- **RxNav API**:  
  - Provides a comprehensive database of active ingredients in medications.  
  - Official documentation: [RxNav API](https://lhncbc.nlm.nih.gov/RxNav/APIsOverview.html).  

- **OpenFDA API**:  
  - Offers access to FDA drug, device, and food databases for additional validation and matching.  
  - Official documentation: [OpenFDA API](https://api.fda.gov).  

### **2. Supabase Integration**:  
- Supabase is used to store:  
  - Uploaded image metadata  
  - Recognized text  
  - Matched active ingredients  
  - User interaction history (optional)  
- Learn more: [Supabase Documentation](https://supabase.com/docs).  

---

## **Usage**  

1. Start the Django server:  
   ```bash
   python manage.py runserver
   ```

2. Open your web browser and navigate to:  
   ```
   http://localhost:8000/
   ```

3. Upload an image containing text.  

4. View the extracted text, matched active ingredients, and metadata.  

---

## **License**  

This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for details.  

---

## **Contact**  

**Author**: Svetlana Perekrestova  
**Email**: [svetlana.perekrestova2@gmail.com](mailto:svetlana.perekrestova2@gmail.com)  

Feel free to reach out with questions, suggestions, or feedback!  
