# Premium Developer Job Board — Design Document

## Purpose
This design document describes the object-oriented architecture for the Premium Developer Job Board. It defines the main components, classes, responsibilities, and interactions needed to implement a secure Django/DRF job board with premium access control, paginated search filters, and bot-resistant signup.

## Architecture Overview
The system follows a modular OOP architecture with clearly separated responsibilities:
- Domain models for users and job listings
- Service classes for filtering, pagination, and security
- DRF serializers and view sets for API data exposure
- Authentication and authorization layers for JWT and premium access
- Frontend UI logic for search, filter persistence, and premium gating

## Key Components

### 1. Domain Layer
#### `User`
- Attributes: `id`, `email`, `is_premium`, `password_hash`, `created_at`
- Responsibilities:
  - Represent authenticated users
  - Expose premium membership state
  - Validate signup details

#### `JobPosting`
- Attributes: `id`, `title`, `company`, `location`, `summary`, `salary_range`, `application_link`, `posted_at`
- Responsibilities:
  - Represent job data
  - Provide safe accessors for sensitive fields when masked

#### `SignupAttempt`
- Attributes: `email`, `password`, `honeypot_field`, `created_at`
- Responsibilities:
  - Track signup attempts and validate honeypot traps
  - Reject submissions with filled honeypot values

### 2. Service Layer
#### `AuthService`
- Responsibilities:
  - Issue and verify JWT tokens
  - Decode token payloads and extract `user_id` and `is_premium`
  - Enforce token expiration and signature validation

#### `PremiumAccessService`
- Responsibilities:
  - Determine if a user may view `salary_range` and `application_link`
  - Provide placeholder text for unauthorized access

#### `SearchService`
- Responsibilities:
  - Build query filters from search text and location selections
  - Support complex multi-filter search conditions
  - Ensure the same filter state can be used with pagination

#### `PaginationService`
- Responsibilities:
  - Manage page size, current page, and result offsets
  - Persist filter state across paginated requests
  - Generate next/previous page metadata for the UI

#### `SecurityService`
- Responsibilities:
  - Validate honeypot fields on signup forms
  - Coordinate SAST and dependency audit readiness
  - Provide centralized security checks for the application

### 3. API Layer
#### `JobPostingSerializer`
- Responsibilities:
  - Serialize `JobPosting` domain objects for API responses
  - Apply field-level masking based on request context
  - Use a custom `get_salary_range()` and `get_application_link()` logic

#### `JobPostingViewSet`
- Responsibilities:
  - Provide list and retrieve endpoints for job postings
  - Accept query parameters for search and location filters
  - Wire `SearchService` and `PaginationService` into DRF responses

#### `SignupView`
- Responsibilities:
  - Handle user registration requests
  - Validate honeypot data using `SecurityService`
  - Create `User` domain instances securely

### 4. Frontend Layer
#### `SearchController`
- Responsibilities:
  - Manage keyword and location filter state in the UI
  - Persist filters during pagination navigation
  - Send queries to the backend and render results

#### `JobCardComponent`
- Responsibilities:
  - Display job title, company, location, and summary
  - Render salary/application content conditionally based on API response
  - Show premium upgrade prompts when sensitive fields are masked

#### `SignupFormComponent`
- Responsibilities:
  - Render hidden honeypot field(s) for bot detection
  - Submit user signup data to the API
  - Surface validation feedback on suspicious submissions

## Object Interaction Flow

### Job listing request flow
1. `JobPostingViewSet` receives a request with JWT and filter params.
2. `AuthService` validates the JWT and retrieves `is_premium`.
3. `SearchService` builds the query set using search and location parameters.
4. `PaginationService` applies pagination to the query set.
5. `JobPostingSerializer` serializes each `JobPosting` and masks fields when `is_premium` is false.
6. The API returns paginated results with preserved filter metadata.

### Signup flow with honeypot
1. `SignupFormComponent` submits signup data including a hidden honeypot field.
2. `SignupView` receives the request and forwards it to `SecurityService`.
3. `SecurityService` rejects requests where the honeypot field is populated.
4. Valid requests create a `User` record and return a success response.

## Class Diagram (Conceptual)
- `User`
- `JobPosting`
- `SignupAttempt`
- `AuthService`
- `PremiumAccessService`
- `SearchService`
- `PaginationService`
- `SecurityService`
- `JobPostingSerializer`
- `JobPostingViewSet`
- `SignupView`
- `SearchController`
- `JobCardComponent`
- `SignupFormComponent`

## Security Design
- Premium access is enforced in the API serializer, not in the UI alone.
- JWT tokens are the source of truth for premium access decisions.
- Honeypot fields are implemented on signup forms to catch bots without impacting valid users.
- SAST and dependency audits are treated as mandatory gates for deployment.

## Design Principles
- Single Responsibility Principle: each class handles one specific concern.
- Open/Closed Principle: services and serializers can be extended for new fields or filters.
- Separation of Concerns: keep domain logic, API logic, and presentation logic separate.
- Defensive Security: sensitive field masking is performed server-side.

## Deployment Considerations
- Run Bandit and pip-audit as part of CI before deployment.
- Ensure JWT secret configuration is stored securely and not checked into source control.
- Validate that pagination state is preserved in both server responses and client routing.

## Glossary
- Premium user: authenticated user with `is_premium = true`.
- Masked field: a salary or apply-link field replaced with a restricted placeholder.
- Honeypot: hidden form field used to trap bots.
- JWT: JSON Web Token used for authentication and authorization.
- DRF: Django REST Framework.

## File / Module Suggestions
- `jobs/models.py`
- `users/models.py`
- `jobs/services.py`
- `users/services.py`
- `jobs/serializers.py`
- `jobs/views.py`
- `users/views.py`
- `frontend/search.js`
- `frontend/signup.js`
- `templates/jobs/list.html`
- `templates/users/signup.html`
