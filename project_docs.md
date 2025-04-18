# PillChecker - Project Documentation

## Project Overview
PillChecker is a FastAPI-based backend service that provides OCR-based medication recognition, integration with BiomedNER for ingredient detection, user authentication via Supabase, and RESTful API endpoints for medication management.

## Architecture

### Component Structure
```
app/
├── api/            # API endpoints and routes
├── core/           # Core business logic and configuration
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic schemas
├── services/       # Business services
├── utils/          # Utility functions
├── static/         # Static assets
└── templates/      # Jinja2 templates
```

### Architectural Dependency Map
```
                                    External Services
                                   ┌─────────────────┐
                                   │   Supabase      │
                                   │   BiomedNER     │
                                   │   OCR Service   │
                                   └────────┬────────┘
                                           │
                                           ▼
┌─────────────────┐              ┌─────────────────┐
│    API Layer    │              │    Services     │
│  (FastAPI)      │◄────────────►│  Integration    │
│ - Auth          │              │ - Authentication│
│ - Medications   │              │ - Storage       │
└───────┬─────────┘              └────────┬────────┘
        │                                 │
        ▼                                 ▼
┌─────────────────┐              ┌─────────────────┐
│  Data Models    │◄────────────►│    Schemas      │
│  (SQLAlchemy)   │              │   (Pydantic)    │
│ - Medication    │              │ - Validation    │
│ - Profile       │              │ - Serialization │
└───────┬─────────┘              └────────┬────────┘
        │                                 │
        └─────────────────┐   ┌──────────┘
                         ▼   ▼
                   ┌─────────────────┐
                   │    Database     │
                   │   (PostgreSQL)  │
                   └─────────────────┘
```

## Database Schema

### Profile Model (`profiles` table)
- `id` (UUID): Primary key, associated with Supabase user ID
- `username` (Text): Unique display name
- `bio` (Text): User's biography or description
- Relationships:
  - `medications`: One-to-many relationship with Medication model

### Medication Model (`medications` table)
- `id` (BigInteger): Primary key
- `profile_id` (UUID): Foreign key to Profile
- `title` (String): Name or title of the medication
- `scan_date` (DateTime): Date when the medication was scanned
- `active_ingredients` (Text): List of active ingredients
- `scanned_text` (Text): Raw text extracted from the scan
- `dosage` (String): Dosage information
- `prescription_details` (JSON): Additional prescription details
- `scan_url` (Text): URL of the uploaded medication scan
- Indexes:
  - `idx_medications_profile_id`: For efficient profile-based queries
  - `idx_medications_scan_date`: For date-based queries
  - `idx_medications_title`: For title searches

## API Structure

### Authentication Endpoints (`/api/v1/auth`)
| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/register` | POST | Register a new user | `UserCreate` (email, password, password_confirm, username) | User ID and message |
| `/login` | POST | Log in a user | OAuth2 form (username/password) | `Token` (access_token, token_type, expires_in, refresh_token) |
| `/logout` | POST | Log out a user | None | Success message |
| `/refresh-token` | POST | Refresh an access token | `RefreshToken` (refresh_token) | `Token` (new tokens) |
| `/password-reset/request` | POST | Request a password reset | `EmailRequest` (email) | Success message |
| `/password-reset/verify` | POST | Reset password with token | `PasswordReset` (token, new_password, new_password_confirm) | Success message |
| `/verify-email` | GET | Verify email address | `token` (query param) | Success message |
| `/create-profile` | POST | Create user profile | `ProfileCreate` (username) | Profile details |

### Medication Endpoints (`/api/v1/medications`)
| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/upload` | POST | Upload and process medication image | Image file | `MedicationResponse` |
| `/list` | GET | List user medications | Query params (page, size) | `PaginatedResponse` of medications |
| `/{medication_id}` | GET | Get medication by ID | Path param (medication_id) | `MedicationResponse` |
| `/recent` | GET | Get recent medications | Query param (limit) | List of `MedicationResponse` |

## Services Integration

### 1. OCR Service (EasyOCR)
The application uses EasyOCR to extract text from medication images. The OCR service is implemented as a pluggable architecture with:
- Abstract `OCRClient` base class
- Concrete `EasyOCRClient` implementation
- Factory functions for obtaining and setting the OCR client

### 2. BiomedNER Service
Integration with BiomedNER service for detecting active ingredients in medication text:
- `MedicalNERClient` makes HTTP requests to the BiomedNER API
- Environment variables control the BiomedNER service host and scheme

### 3. Supabase Integration
The application uses Supabase for:
- Authentication: User signup, login, password reset
- Storage: Storing medication images
- Database: PostgreSQL database for application data

## User Flow

1. **User Registration and Authentication**
   - User registers via `/api/v1/auth/register` endpoint
   - Email verification (if enabled)
   - User logs in via `/api/v1/auth/login` endpoint
   - JWT token is used for subsequent authenticated requests

2. **Medication Upload and Processing**
   - User uploads a medication image via `/api/v1/medications/upload` endpoint
   - Image is processed with OCR to extract text
   - Extracted text is analyzed with BiomedNER to identify active ingredients
   - Medication record is created in the database

3. **Medication Management**
   - User can view their medications via:
     - List: `/api/v1/medications/list` (paginated)
     - Details: `/api/v1/medications/{medication_id}`
     - Recent: `/api/v1/medications/recent` (most recent N medications)

4. **Web Interface**
   - The application also provides a minimal web interface with pages for:
     - Home (`/`)
     - Login (`/login`)
     - Registration (`/register`)
     - Dashboard (`/dashboard`)
     - Medication Details (`/medication/{medication_id}`)

## Deployment

### Docker Configuration
The application uses a multi-stage Docker build for optimized image size:
1. Builder stage installs dependencies
2. Final stage includes only runtime dependencies
3. Health check ensures the application is running correctly
4. Configuration via environment variables

### Environment Variables
Key environment variables required by the application:
- `APP_ENV`: Application environment (development, testing, production)
- `SECRET_KEY`: Secret key for security features
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase API key
- `DATABASE_*`: Database connection details (user, password, host, port, name)
- `BIOMED_HOST`: BiomedNER service host
- `BIOMED_SCHEME`: BiomedNER service scheme (http/https)

## UML Class Diagram

```
┌───────────────────────┐       ┌───────────────────────┐
│        Profile        │       │      Medication       │
├───────────────────────┤       ├───────────────────────┤
│ +id: UUID (PK)        │       │ +id: BigInteger (PK)  │
│ +username: String     │  1:N  │ +profile_id: UUID (FK)│
│ +bio: String          │◄──────┤ +title: String        │
├───────────────────────┤       │ +scan_date: DateTime  │
│ +__repr__()           │       │ +active_ingredients:  │
└───────────────────────┘       │  String               │
                                │ +scanned_text: String │
                                │ +dosage: String       │
                                │ +prescription_details:│
                                │  JSON                 │
                                │ +scan_url: String     │
                                ├───────────────────────┤
                                │ +__repr__()           │
                                └───────────────────────┘

┌─────────────────────────┐     ┌────────────────────┐
│     EasyOCRClient       │     │     OCRClient      │
├─────────────────────────┤     ├────────────────────┤
│ -reader: EasyOCR Reader │     │ +read_text(image)  │
├─────────────────────────┤     └────────────────────┘
│ +read_text(image)       │              ▲
└──────────┬──────────────┘              │
           │ implements                  │
           └──────────────────────────────
```
