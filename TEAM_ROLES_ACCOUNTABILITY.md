# Team Roles & Accountability

This document defines the responsibilities and defense talking points for the five-member enterprise software team. Each role is assigned a distinct technical domain and individual grading will focus on the candidate's mastery of that area.

## 1. Lead Cloud & DevOps Engineer

### Core Responsibilities
- Deploy the application to Render or Railway.
- Configure cloud media storage using Cloudinary.
- Secure environment variables and protect secrets in production.
- Create CI/CD-ready deployment steps and document the pipeline.

### Defense Script
- Explain the deployment architecture and why you chose Render or Railway.
- Describe how environment variables are managed securely and why secrets should never be hard-coded.
- Walk through how Cloudinary is integrated for media uploads and why it was chosen for cloud media.
- Highlight any rollback, staging, or zero-downtime practices used during deployment.

### Accountability Checklist
- Deployment success on the selected hosting platform.
- Correct use of secure environment variable storage.
- Cloud media configuration that supports production file handling.
- Clear documentation of deployment and infrastructure decisions.

## 2. API & IAM Engineer

### Core Responsibilities
- Build and maintain the Django REST Framework API.
- Implement JWT authentication for token-based access.
- Design and enforce field-level masking for sensitive data.
- Ensure API endpoints follow secure authentication and authorization practices.
    
### Defense Script
- Describe the DRF architecture and how the API is structured.
- Explain JWT authentication flows, token generation, and token validation.
- Demonstrate field-level masking and why it matters for privacy and compliance.
- Show how authenticated users are differentiated from anonymous users and how permissions are enforced.

### Accountability Checklist
- Reliable DRF endpoints for core application workflows.
- Secure JWT implementation with correct token handling.
- Field-level masking protecting sensitive fields in API responses.
- Clear separation of API and identity management concerns.

## 3. Database Architect & RBAC Lead

### Core Responsibilities
- Design the database schema and relationships for the project.
- Enforce Anti-IDOR logic to prevent insecure direct object references.
- Manage bulk database operations safely and efficiently.
- Implement role-based access control (RBAC) rules in the data layer.

### Defense Script
- Present the data model and explain why relationships were designed that way.
- Describe the Anti-IDOR checks and how they prevent unauthorized data access.
- Discuss bulk database operations and how you maintain data integrity during updates.
- Explain RBAC rules and how they are enforced at the model or service layer.

### Accountability Checklist
- Logical and maintainable database design.
- Active Anti-IDOR validation on sensitive record access.
- Bulk operations that preserve consistency and performance.
- RBAC enforcement across relevant models and views.

## 4. Frontend UI & Component Engineer

### Core Responsibilities
- Build advanced dashboard interfaces for users and admins.
- Create interactive filtering, formsets, and reusable UI components.
- Develop custom Django template tags as needed.
- Ensure responsive design and a polished user experience.

### Defense Script
- Walk through the dashboard UI and its main user journeys.
- Explain interactive filters and how users refine data on the page.
- Show formsets or dynamic form behavior that improves usability.
- Describe any custom template tags and why they were created.

### Accountability Checklist
- Intuitive dashboard with clean component structure.
- Interactive filter mechanics that work smoothly.
- Reusable template tags and front-end components.
- Evidence of user-focused interface decisions.

## 5. DevSecOps & Compliance Analyst

### Core Responsibilities
- Implement active defenses like `django-axes` and honeypots.
- Enable Python audit logging for security events.
- Run SAST and dependency scans; document findings.
- Review and enforce secure coding and compliance controls.

### Defense Script
- Explain how `django-axes` or other active defenses block attacks.
- Describe honeypot placement and what threats it catches.
- Talk through audit logging coverage for Python/Django security events.
- Show the SAST/dependency scanning tools used and how vulnerabilities were addressed.

### Accountability Checklist
- Active defenses configured and working.
- Audit logging in place for critical operations.
- SAST/dependency scan results documented and remediated.
- Compliance reasoning for security controls.

## How to Use This Script
- Assign one role to each member of the group.
- Each member should internalize their role's responsibilities and defense script.
- During the face-to-face defense, answer questions with facts, architecture logic, and concrete examples.
- Use the accountability checklists to validate that implementation matches the role.

## Grading Focus
- Individual mastery of assigned role.
- Clear explanation of design and implementation decisions.
- Demonstrated understanding of security, scalability, and maintainability.
- Ability to connect role responsibilities to the actual project implementation.
