# Upsight Backend API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Management App](#management-app)
4. [Board App](#board-app)
5. [Authentication System](#authentication-system)
6. [Permission System](#permission-system)
7. [API Endpoints](#api-endpoints)
8. [Core Business Logic](#core-business-logic)
9. [Data Validation](#data-validation)

---

## Overview

The Upsight backend is a Django REST Framework-based system designed to manage educational institutions, students, employees, and content distribution. The system consists of two main applications:

- **Management App**: Handles user management, authentication, educational entities, and administrative functions
- **Board App**: Manages content distribution including news, notices, translations, and information documents

### Key Features

- **Multi-language Support**: Korean (KO) and Uzbek (UZ) language support throughout the system
- **Role-based Access Control**: Multiple user roles with specific permissions
- **JWT Authentication**: Secure token-based authentication system
- **File Management**: Support for document and image uploads with validation
- **University-scoped Data**: Content and access control based on university associations

---

## Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐
│  Management App │    │    Board App    │
│                 │    │                 │
│ • Authentication│    │ • News          │
│ • User Management│   │ • Notices       │
│ • Students      │    │ • Translations  │
│ • Employees     │    │ • Information   │
│ • Universities  │    │ • Documents     │
│ • Classes       │    │                 │
│ • Careers       │    │                 │
└─────────────────┘    └─────────────────┘
        │                       │
        └───────┬───────────────┘
                │
        ┌───────▼───────┐
        │  Shared Models │
        │               │
        │ • University  │
        │ • Permissions │
        └───────────────┘
```

### Technology Stack

- **Backend**: Django 4.x + Django REST Framework
- **Authentication**: JWT (SimpleJWT)
- **Admin Interface**: Django Unfold
- **File Storage**: Local file system with validation
- **Database**: SQLite/PostgreSQL (configurable)

---

## Management App

The Management app serves as the core administrative system handling user authentication, student/employee management, and educational program coordination.

### Models Overview

#### Core Entity Models

##### [`University`](management/models.py:8)
Represents educational institutions with bilingual support.

```python
class University(models.Model):
    name_ko = models.CharField(max_length=100)  # Korean name
    name_uz = models.CharField(max_length=100)  # Uzbek name
    grade = models.CharField(choices=GRADE_OPTIONS)  # best, excellent, average, low
    years = models.CharField(choices=YEARS_OPTIONS)  # 2 years, 4 years
    representative_ko = models.CharField(max_length=100)
    representative_uz = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contract = models.CharField(choices=CONTRACT_OPTIONS)  # yes, no
    agreement_date = models.DateField()
    logo = models.ImageField(upload_to='university_logos/')
```

**Key Features**:
- Bilingual name support (Korean/Uzbek)
- University grading system
- Contract management
- Logo upload with size validation (5MB limit)

##### [`Student`](management/models.py:48)
Student management with comprehensive personal and educational information.

```python
class Student(models.Model):
    # Personal Information
    name_ko = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(choices=GENDER_CHOICES)
    
    # Educational Background
    high_school = models.CharField(max_length=200)
    college = models.CharField(max_length=200)
    university = models.CharField(max_length=200)
    
    # Guardian Information
    guardian_name_ko = models.CharField(max_length=100)
    guardian_name_uz = models.CharField(max_length=100)
    guardian_relationship = models.CharField(choices=RELATIONSHIP_CHOICES)
    
    # Authentication
    student_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
```

**Key Features**:
- Complete personal profile management
- Educational background tracking
- Guardian information for minors
- Simple authentication system (not Django User integration)
- Document attachment support via [`AttachedDocument`](management/models.py:106)

##### [`Employee`](management/models.py:134)
Employee management with Django User integration and role-based access.

```python
class Employee(models.Model):
    # Personal Information
    name_ko = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100)
    position = models.CharField(choices=POSITION_CHOICES)
    
    # Employment Details
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=STATUS_CHOICES, default="Work")
    
    # Authentication Integration
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=50, unique=True)
```

**Core Logic**:
- **Auto User Creation**: When an employee is created, a Django User is automatically generated
- **Group Assignment**: Employees are automatically added to `upsight_staff` group
- **Password Hashing**: Passwords are automatically hashed using Django's system

```python
def save(self, *args, **kwargs):
    is_new = self.pk is None
    if is_new:
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
    
    super().save(*args, **kwargs)
    if is_new:
        user = User.objects.create(
            username=self.employee_id,
            email=self.email,
            first_name=self.name_ko or self.name_uz,
            password=self.password,
            is_active=True,
            is_staff=True,
        )
        upsight_staff_group, _ = Group.objects.get_or_create(name="upsight_staff")
        user.groups.add(upsight_staff_group)
        self.user = user
```

#### Educational Management Models

##### [`Class`](management/models.py:378)
Course/class management with teacher assignments and scheduling.

```python
class Class(models.Model):
    teacher_first = models.ForeignKey(Employee, related_name='classes_first')
    teacher_second = models.ForeignKey(Employee, related_name='classes_second')
    level = models.CharField(choices=LEVEL_OPTIONS)  # low, intermediate, high
    lecture = models.CharField(choices=LECTURE_OPTIONS)  # topik, aboard, nurse, it, others
    opening_date = models.DateField()
    period = models.IntegerField()  # months
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2)
```

##### [`ClassTimeTable`](management/models.py:444)
Flexible scheduling system with multi-day support.

```python
class ClassTimeTable(models.Model):
    WEEKDAY_CHOICES = [
        ("monday", "월요일 / Душанба"),    # Korean / Uzbek
        ("tuesday", "화요일 / Сешанба"),
        # ... other days
    ]
    
    class_model = models.ForeignKey(Class, related_name='timetables')
    days = models.CharField(max_length=100, choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
```

**Key Features**:
- Bilingual day names (Korean/Uzbek)
- Multiple time slots per class
- Duration calculation in serializers

##### [`Enterance`](management/models.py:264) (University Entrance Management)
Manages university entrance programs and student registrations.

```python
class Enterance(models.Model):
    university = models.ForeignKey(University, related_name='entrances')
    years = models.IntegerField(choices=YEAR_OPTIONS)
    kind = models.CharField(choices=KIND_OPTIONS)  # language, collegue, university, graduate
    order = models.CharField(choices=ORDER_OPTIONS)  # 1st, 2nd, 3rd, 4th, spring, winter
    from_date = models.DateField()
    to_date = models.DateField()
    state = models.CharField(choices=STATE_OPTIONS)  # end, now, after
```

#### Career Management Models

##### [`Career`](management/models.py:677)
Career counseling and job placement tracking.

```python
class Career(models.Model):
    name_ko = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(choices=(("male", "Male"), ("female", "Female")))
```

**Related Models**:
- [`CareerHistory`](management/models.py:694): Work history tracking
- [`CareerCounsel`](management/models.py:705): Counseling session records

### API Endpoints (Management)

#### Authentication Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | [`/api/management/auth/login`](management/views.py:40) | Employee login with JWT | Public |
| POST | [`/api/management/auth/logout`](management/views.py:70) | Token blacklisting | Authenticated |
| GET | [`/api/management/auth/profile`](management/views.py:85) | Current user profile | Authenticated |

#### Student Management

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | [`/api/management/students`](management/views.py:101) | List students | upsight_staff (full), others (limited) |
| GET | [`/api/management/students/<id>`](management/views.py:331) | Student details | upsight_staff |

#### Employee Management

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | [`/api/management/employees`](management/views.py:273) | List employees | upsight_staff |
| GET | [`/api/management/employees/<id>`](management/views.py:302) | Employee details | upsight_staff |

#### University Management

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | [`/api/management/universities`](management/views.py:215) | List universities | upsight_staff |
| GET | [`/api/management/universities/<id>`](management/views.py:244) | University details | upsight_staff |

### Core Business Logic (Management)

#### User Access Control
The system implements role-based access with the following logic:

```python
def students_list(request):
    is_upsight_staff = request.user.groups.filter(name="upsight_staff").exists()
    
    if is_upsight_staff:
        students = Student.objects.all()  # Full access
    else:
        students = Student.objects.all()[:1]  # Limited access
```

#### JWT Token Generation
Custom JWT tokens include employee-specific information:

```python
def get_tokens_for_user(employee):
    refresh = RefreshToken.for_user(employee.user)
    refresh["employee_id"] = employee.employee_id
    refresh["role"] = employee.user.groups.first().name if employee.user.groups.first() else "user"
    
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
```

---

## Board App

The Board app manages content distribution and information sharing across universities with role-based content access.

### Models Overview

#### Content Models

##### [`News`](board/models.py:5)
News article management with university association.

```python
class News(models.Model):
    title_uz = models.CharField(max_length=200)
    title_ko = models.CharField(max_length=200)
    content_uz = models.TextField()
    content_ko = models.TextField()
    image = models.ImageField(upload_to='news_images/')
    date = models.DateTimeField(auto_now_add=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
```

##### [`Notice`](board/models.py:18)
Official notices and announcements.

```python
class Notice(models.Model):
    title_uz = models.CharField(max_length=200)
    title_ko = models.CharField(max_length=200)
    content_uz = models.TextField()
    content_ko = models.TextField()
    image = models.ImageField(upload_to='notice_images/')
    university = models.ForeignKey(University, on_delete=models.CASCADE)
```

##### [`Translation`](board/models.py:31)
Translation services and language-related content.

##### [`Information`](board/models.py:43)
General information with document attachments.

```python
class Information(models.Model):
    title_uz = models.CharField(max_length=200)
    title_ko = models.CharField(max_length=200)
    content_uz = models.TextField()
    content_ko = models.TextField()
    university = models.ForeignKey(University, on_delete=models.CASCADE)
```

**Related Model**:
- [`InformationDocuments`](board/models.py:56): File attachments for information items

### API Endpoints (Board)

#### News Management

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | [`/api/board/news`](board/views.py:46) | List news | upsight_staff, university_staff |
| GET | [`/api/board/news/<id>`](board/views.py:78) | News details | upsight_staff, university_staff |
| POST | [`/api/board/news/create`](board/views.py:117) | Create news | upsight_staff, university_staff |
| PUT/PATCH | [`/api/board/news/<id>/update`](board/views.py:167) | Update news | upsight_staff, university_staff |
| DELETE | [`/api/board/news/<id>/delete`](board/views.py:232) | Delete news | upsight_staff, university_staff |

#### Similar endpoints exist for Notices, Translations, Information, and Information Documents

### Core Business Logic (Board)

#### Permission-based Content Filtering
The board app implements university-scoped content access:

```python
def filter_by_permissions(queryset, user):
    if user.groups.filter(name="upsight_staff").exists():
        return queryset  # upsight_staff can see all
    
    university = get_user_university(user)
    if university:
        return queryset.filter(university=university)  # university_staff sees only their content
    
    return queryset.none()  # No access if no proper role
```

#### University Staff Association
University staff users are linked to specific universities:

```python
def get_user_university(user):
    try:
        if user.groups.filter(name="university_staff").exists():
            manager = UniversityManager.objects.get(user=user)
            return manager.university
    except UniversityManager.DoesNotExist:
        pass
    return None
```

---

## Authentication System

### JWT Implementation

The system uses Django REST Framework SimpleJWT with custom token payloads:

#### Login Flow
1. Employee provides `employee_id` and `password`
2. System validates credentials against [`Employee`](management/models.py:134) model
3. Custom JWT tokens are generated with employee metadata
4. Tokens include `employee_id` and `role` information

#### Token Structure
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "EMP001",
    "email": "employee@example.com",
    "name": "Employee Name",
    "role": "upsight_staff"
  }
}
```

### Password Security
- Employee passwords are hashed using Django's `make_password()`
- Students use simple password storage (not Django User integrated)
- Automatic password hashing on employee creation

---

## Permission System

### User Groups

#### `upsight_staff`
- **Access Level**: Full system access
- **Capabilities**: 
  - View all students, employees, universities
  - Manage all content across universities
  - Administrative functions

#### `university_staff`
- **Access Level**: University-scoped access
- **Capabilities**:
  - View only their university's content
  - Manage news, notices, translations for their university
  - Limited student/employee access

#### Permission Enforcement

```python
# Example permission check in views
if not (request.user.groups.filter(name="upsight_staff").exists() or 
        request.user.groups.filter(name="university_staff").exists()):
    return Response({"error": "Permission denied"}, status=403)

# University-scoped content check
if request.user.groups.filter(name="university_staff").exists():
    user_university = get_user_university(request.user)
    if user_university != content.university:
        return Response({"error": "Permission denied"}, status=403)
```

---

## API Endpoints Summary

### Management App Endpoints

```
Authentication:
POST   /api/management/auth/login              # Employee login
POST   /api/management/auth/logout             # Logout
GET    /api/management/auth/profile            # User profile

Students:
GET    /api/management/students                # List students
GET    /api/management/students/<id>           # Student details

Employees:
GET    /api/management/employees               # List employees
GET    /api/management/employees/<id>          # Employee details

Universities:
GET    /api/management/universities            # List universities
GET    /api/management/universities/<id>       # University details

Classes:
GET    /api/management/classes                 # List classes
GET    /api/management/classes/<id>            # Class details
GET    /api/management/classes/<id>/timetables # Class schedules

Other entities:
GET    /api/management/enterances              # University entrances
GET    /api/management/organs                  # Partner organizations
GET    /api/management/careers                 # Career counseling
```

### Board App Endpoints

```
News:
GET    /api/board/news                         # List news
POST   /api/board/news/create                  # Create news
GET    /api/board/news/<id>                    # News details
PUT    /api/board/news/<id>/update             # Update news
DELETE /api/board/news/<id>/delete             # Delete news

Notices:
GET    /api/board/notices                      # List notices
POST   /api/board/notices/create               # Create notice
GET    /api/board/notices/<id>                 # Notice details
PUT    /api/board/notices/<id>/update          # Update notice
DELETE /api/board/notices/<id>/delete          # Delete notice

Translations:
GET    /api/board/translations                 # List translations
POST   /api/board/translations/create          # Create translation
GET    /api/board/translations/<id>            # Translation details
PUT    /api/board/translations/<id>/update     # Update translation
DELETE /api/board/translations/<id>/delete     # Delete translation

Information:
GET    /api/board/information                  # List information
POST   /api/board/information/create           # Create information
GET    /api/board/information/<id>             # Information details
PUT    /api/board/information/<id>/update      # Update information
DELETE /api/board/information/<id>/delete      # Delete information

Information Documents:
GET    /api/board/information-documents        # List documents
POST   /api/board/information-documents/create # Create document
GET    /api/board/information-documents/<id>   # Document details
PUT    /api/board/information-documents/<id>/update # Update document
DELETE /api/board/information-documents/<id>/delete # Delete document
```

---

## Data Validation

### File Upload Validation

The system includes comprehensive file validation through [`management/validators.py`](management/validators.py):

#### Image Validation
```python
def validate_image_size(file):
    max_size = 5 * 1024 * 1024  # 5MB for images
    if file.size > max_size:
        raise ValidationError("Image size cannot exceed 5MB.")
```

#### Document Validation
```python
def validate_pdf_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext != ".pdf":
        raise ValidationError("Only PDF files are allowed.")

def validate_file_size(file):
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if file.size > max_size:
        raise ValidationError("File size cannot exceed 10MB.")
```

### Serializer Validation

#### Content Validation (Board App)
All content models require at least one language version:

```python
def validate(self, data):
    if not data.get('title_uz') and not data.get('title_ko'):
        raise serializers.ValidationError("At least one title (UZ or KO) is required.")
    if not data.get('content_uz') and not data.get('content_ko'):
        raise serializers.ValidationError("At least one content (UZ or KO) is required.")
    return data
```

#### Schedule Validation
Class timetables include time validation:

```python
def validate(self, data):
    if data.get("start_time") and data.get("end_time"):
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError("End time must be after start time.")
    return data
```

---

## Key Design Patterns

### 1. Bilingual Content Support
All user-facing content supports Korean (KO) and Uzbek (UZ) with fallback logic:

```python
def get_name(self, obj):
    return obj.name_ko or obj.name_uz  # Korean preferred, Uzbek fallback
```

### 2. University-scoped Access Control
Content and access are consistently scoped by university association:

```python
# Automatic university assignment for university_staff
if request.user.groups.filter(name="university_staff").exists():
    user_university = get_user_university(request.user)
    data['university'] = user_university.id
```

### 3. Comprehensive Error Handling
All API endpoints include consistent error handling:

```python
try:
    # Operation logic
    return Response(data, status=status.HTTP_200_OK)
except ModelName.DoesNotExist:
    return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
except Exception as e:
    return Response(
        {"error": "Operation failed", "details": str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
```

### 4. Related Object Optimization
Database queries are optimized using `select_related` and `prefetch_related`:

```python
# Efficient querying
news = News.objects.select_related('university').all()
information = Information.objects.select_related('university').prefetch_related('documents').all()
```

This documentation provides a comprehensive overview of the Upsight backend system's architecture, functionality, and implementation details.