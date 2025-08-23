from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password

from .validators import validate_image_size, validate_pdf_file, validate_file_size


class University(models.Model):
    GRADE_OPTIONS = (
        ("best", "Best"),
        ("excellent", "Excellent"),
        ("average", "Average"),
        ("low", "Low"),
    )
    YEARS_OPTIONS = (("2", "2 years"), ("4", "4 years"))
    CONTRACT_OPTIONS = (("yes", "YES"), ("no", "NO"))
    name_ko = models.CharField(max_length=100, verbose_name="Name (Korean)")
    name_uz = models.CharField(max_length=100, verbose_name="Name (Uzbek)")
    grade = models.CharField(
        max_length=50, blank=True, null=True, choices=GRADE_OPTIONS
    )
    years = models.CharField(
        max_length=50, blank=True, null=True, choices=YEARS_OPTIONS
    )
    representative_uz = models.CharField(max_length=100, blank=True, null=True)
    representative_ko = models.CharField(max_length=100, blank=True, null=True)
    position_uz = models.CharField(max_length=100, blank=True, null=True)
    position_ko = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(unique=True)
    contract = models.CharField(
        max_length=100, blank=True, null=True, choices=CONTRACT_OPTIONS
    )
    agreement_date = models.DateField()
    logo = models.ImageField(
        upload_to="university_logos/",
        validators=[validate_image_size],
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.name_ko} / {self.name_uz}"


class Student(models.Model):
    GENDER_CHOICES = [("M", "Male"), ("F", "Female")]
    RELATIONSHIP_CHOICES = [("F", "Father"), ("M", "Mother")]

    # Personal Information
    name_ko = models.CharField(max_length=100, verbose_name="Name (Korean)")
    name_uz = models.CharField(max_length=100, verbose_name="Name (Uzbek)")
    birth_date = models.DateField()

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    telephone = models.CharField(max_length=20)
    address = models.TextField()
    email = models.EmailField()
    picture = models.ImageField(
        upload_to="student_images/",
        validators=[validate_image_size],
        blank=True,
        null=True,
    )

    # Education Background
    high_school = models.CharField(max_length=200, blank=True, null=True)
    college = models.CharField(max_length=200, blank=True, null=True)
    university = models.CharField(max_length=200, blank=True, null=True)
    master = models.CharField(max_length=200, blank=True, null=True)
    other_education = models.CharField(max_length=200, blank=True, null=True)

    # Guardian Information
    guardian_name_ko = models.CharField(
        max_length=100, verbose_name="Guardian Name (Korean)"
    )
    guardian_name_uz = models.CharField(
        max_length=100, verbose_name="Guardian Name (Uzbek)"
    )
    guardian_telephone = models.CharField(max_length=20)
    guardian_relationship = models.CharField(max_length=1, choices=RELATIONSHIP_CHOICES)

    # Authentication (simple fields, not Django User integration)
    student_id = models.CharField(max_length=50, unique=True, verbose_name="Student ID")
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_name(self, language="ko"):
        return self.name_ko if language == "ko" else self.name_uz

    def get_guardian_name(self, language="ko"):
        return self.guardian_name_ko if language == "ko" else self.guardian_name_uz

    def __str__(self):
        return f"{self.name_ko or self.name_uz} ({self.student_id})"

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ["-created_at"]


class AttachedDocument(models.Model):
    student = models.ForeignKey(
        Student, related_name="attached_documents", on_delete=models.CASCADE
    )
    document_name_ko = models.CharField(
        max_length=200, verbose_name="Document Name (Korean)"
    )
    document_name_uz = models.CharField(
        max_length=200, verbose_name="Document Name (Uzbek)"
    )
    file = models.FileField(
        upload_to="student_documents/",
        validators=[validate_pdf_file, validate_file_size],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def get_document_name(self, language="ko"):
        return self.document_name_ko if language == "ko" else self.document_name_uz

    def __str__(self):
        return f"{self.document_name_ko or self.document_name_uz} - {self.student}"

    class Meta:
        verbose_name = "Attached Document"
        verbose_name_plural = "Attached Documents"
        ordering = ["-uploaded_at"]


class Employee(models.Model):
    GENDER_CHOICES = [("M", "Male"), ("F", "Female")]
    POSITION_CHOICES = [
        ("Teacher", "Teacher"),
        ("Staff", "Staff"),
        ("Manager", "Manager"),
        ("Director", "Director"),
        ("Other", "Other"),
    ]
    STATUS_CHOICES = [
        ("Work", "Work"),
        ("End", "End"),
        ("Rest", "Rest"),
    ]

    # Personal Information
    name_ko = models.CharField(max_length=100, verbose_name="Name (Korean)")
    name_uz = models.CharField(max_length=100, verbose_name="Name (Uzbek)")
    birth_date = models.DateField(verbose_name="Birthday")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    start_date = models.DateField(verbose_name="Start Date")
    telephone = models.CharField(max_length=20)
    address = models.TextField()
    email = models.EmailField()

    # Education Background
    college = models.CharField(max_length=200, blank=True, null=True)
    university = models.CharField(max_length=200, blank=True, null=True)
    graduate = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Graduate"
    )

    # Employment Details
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="Work", verbose_name="Status"
    )

    # Profile Picture
    picture = models.ImageField(
        upload_to="employee_images/",
        validators=[validate_image_size],
        blank=True,
        null=True,
    )

    # Authentication
    employee_id = models.CharField(max_length=50, unique=True, verbose_name="ID")
    password = models.CharField(max_length=128)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="employee_profile",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Check if this is a new employee (no primary key yet)
        is_new = self.pk is None

        if is_new:
            # Hash the password before saving
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

            upsight_staff_group, created = Group.objects.get_or_create(
                name="upsight_staff"
            )
            user.groups.add(upsight_staff_group)
            self.user = user
            super().save(update_fields=["user"])

    def get_name(self, language="ko"):
        return self.name_ko if language == "ko" else self.name_uz

    def __str__(self):
        return f"{self.name_ko or self.name_uz} ({self.employee_id})"

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ["-created_at"]


class EmployeeDocument(models.Model):
    employee = models.ForeignKey(
        Employee, related_name="attached_documents", on_delete=models.CASCADE
    )
    document_name_ko = models.CharField(
        max_length=200, verbose_name="Document Name (Korean)"
    )
    document_name_uz = models.CharField(
        max_length=200, verbose_name="Document Name (Uzbek)"
    )
    file = models.FileField(
        upload_to="employee_documents/",
        validators=[validate_pdf_file, validate_file_size],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def get_document_name(self, language="ko"):
        return self.document_name_ko if language == "ko" else self.document_name_uz

    def __str__(self):
        return f"{self.document_name_ko or self.document_name_uz} - {self.employee}"

    class Meta:
        verbose_name = "Employee Document"
        verbose_name_plural = "Employee Documents"
        ordering = ["-uploaded_at"]


class Enterance(models.Model):
    YEAR_OPTIONS = (
        (2026, "2026"),
        (2027, "2027"),
        (2028, "2028"),
        (2029, "2029"),
        (2030, "2030"),
    )
    KIND_OPTIONS = (
        ("language", "Language"),
        ("collegue", "Collegue"),
        ("university", "University"),
        ("graduate", "Graduate"),
    )
    ORDER_OPTIONS = (
        ("1", "1st"),
        ("2", "2nd"),
        ("3", "3rd"),
        ("4", "4th"),
        ("spring", "Spring"),
        ("winter", "Winter"),
    )
    STATE_OPTIONS = (
        ("end", "End"),
        ("now", "Now"),
        ("after", "After"),
    )
    university = models.ForeignKey(
        University, related_name="entrances", on_delete=models.CASCADE
    )
    years = models.IntegerField(verbose_name="Years", choices=YEAR_OPTIONS)
    kind = models.CharField(
        max_length=50, verbose_name="Kind of Entrance", choices=KIND_OPTIONS
    )
    order = models.CharField(max_length=50, verbose_name="Order", choices=ORDER_OPTIONS)
    from_date = models.DateField(verbose_name="Period from")
    to_date = models.DateField(verbose_name="Period to")
    contract_no = models.CharField(
        max_length=100, verbose_name="Contract No", blank=True, null=True
    )
    state = models.CharField(max_length=50, verbose_name="State", choices=STATE_OPTIONS)


class EnteranceStudentRegistration(models.Model):
    STATE_OPTIONS = (
        (1, "Go"),
        (2, "Pass"),
        (3, "NP"),
    )
    enterance = models.ForeignKey(
        Enterance, related_name="student_registrations", on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        Student, related_name="enterance_registrations", on_delete=models.CASCADE
    )
    date = models.DateField(verbose_name="Date")
    contract = models.CharField(
        max_length=100, verbose_name="Contract No", blank=True, null=True
    )
    bonus = models.CharField(
        max_length=100, verbose_name="Bonus", blank=True, null=True
    )
    state = models.IntegerField(verbose_name="State", choices=STATE_OPTIONS)
    recommend = models.CharField(
        max_length=100, verbose_name="Recommendation", blank=True, null=True
    )

    class Meta:
        verbose_name = "Entrance Student Registration"
        verbose_name_plural = "Entrance Student Registrations"
        unique_together = ("enterance", "student")


class EnterancePayment(models.Model):
    date = models.DateField(verbose_name="Payment Date")
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Payment Amount"
    )
    student = models.ForeignKey(
        Student, related_name="payments", on_delete=models.CASCADE
    )
    enterance = models.ForeignKey(
        Enterance, related_name="consulting_payments", on_delete=models.CASCADE
    )


class EnteranceDocument(models.Model):
    enterance = models.ForeignKey(
        Enterance, related_name="attached_documents", on_delete=models.CASCADE
    )
    document_name_ko = models.CharField(
        max_length=200, verbose_name="Document Name (Korean)"
    )
    document_name_uz = models.CharField(
        max_length=200, verbose_name="Document Name (Uzbek)"
    )
    file = models.FileField(
        upload_to="student_documents/",
        validators=[validate_pdf_file, validate_file_size],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def get_document_name(self, language="ko"):
        return self.document_name_ko if language == "ko" else self.document_name_uz

    def __str__(self):
        return f"{self.document_name_ko or self.document_name_uz} - {self.student}"

    class Meta:
        verbose_name = "Attached Document"
        verbose_name_plural = "Attached Documents"
        ordering = ["-uploaded_at"]


class Class(models.Model):
    LEVEL_OPTIONS = (
        ("low", "Low"),
        ("intermediate", "Intermediate"),
        ("high", "High"),
    )
    LECTURE_OPTIONS = (
        ("topik", "TOPIK"),
        ("aboard", "Aboard"),
        ("nurse", "Nurse"),
        ("it", "IT"),
        ("others", "Others"),
    )
    GROUP_OPTIONS = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7"),
        (8, "8"),
        (9, "9"),
        (10, "10"),
    )
    PERIOD_OPTIONS = (
        (1, "1"),
        (3, "3"),
        (6, "6"),
    )
    teacher_first = models.ForeignKey(
        Employee, related_name="classes_first", on_delete=models.CASCADE
    )
    teacher_second = models.ForeignKey(
        Employee, related_name="classes_second", on_delete=models.CASCADE
    )
    level = models.CharField(
        max_length=100, verbose_name="Level", choices=LEVEL_OPTIONS
    )
    lecture = models.CharField(
        max_length=100, verbose_name="Lecture", choices=LECTURE_OPTIONS
    )
    group = models.IntegerField(
        verbose_name="Group", blank=True, null=True, choices=GROUP_OPTIONS
    )
    opening_date = models.DateField(verbose_name="Opening date")
    period = models.IntegerField(
        verbose_name="Period (in months)",
    )
    tuition_fee = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Tuition Fee"
    )
    textbook_first = models.CharField(
        max_length=200, verbose_name="Textbook 1", blank=True, null=True
    )
    textbook_second = models.CharField(
        max_length=200, verbose_name="Textbook 2", blank=True, null=True
    )
    classroom = models.CharField(
        max_length=100, verbose_name="Classroom", blank=True, null=True
    )

    def __str__(self):
        return f"{self.classroom} ({self.opening_date})"


class ClassTimeTable(models.Model):
    WEEKDAY_CHOICES = [
        ("monday", "월요일 / Душанба"),  # Monday
        ("tuesday", "화요일 / Сешанба"),  # Tuesday
        ("wednesday", "수요일 / Чоршанба"),  # Wednesday
        ("thursday", "목요일 / Пайшанба"),  # Thursday
        ("friday", "금요일 / Жума"),  # Friday
        ("saturday", "토요일 / Шанба"),  # Saturday
        ("sunday", "일요일 / Якшанба"),  # Sunday
    ]

    class_model = models.ForeignKey(
        Class, related_name="timetables", on_delete=models.CASCADE, verbose_name="Class"
    )
    days = models.CharField(
        max_length=100, verbose_name="Days of the Week", choices=WEEKDAY_CHOICES
    )
    start_time = models.TimeField(verbose_name="Start Time")
    end_time = models.TimeField(verbose_name="End Time")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_days_display(self):
        """Get display names for all selected days"""
        day_mapping = dict(self.WEEKDAY_CHOICES)
        return [day_mapping.get(day, day) for day in self.days]

    def get_days_display_ko(self):
        """Get Korean day names"""
        day_mapping = {
            "monday": "월요일",
            "tuesday": "화요일",
            "wednesday": "수요일",
            "thursday": "목요일",
            "friday": "금요일",
            "saturday": "토요일",
            "sunday": "일요일",
        }
        return [day_mapping.get(day, day) for day in self.days]

    def get_days_display_uz(self):
        """Get Uzbek day names"""
        day_mapping = {
            "monday": "Душанба",
            "tuesday": "Сешанба",
            "wednesday": "Чоршанба",
            "thursday": "Пайшанба",
            "friday": "Жума",
            "saturday": "Шанба",
            "sunday": "Якшанба",
        }
        return [day_mapping.get(day, day) for day in self.days]

    def __str__(self):
        days_display = ", ".join(self.get_days_display())
        return f"{days_display} {self.start_time}-{self.end_time}"

    class Meta:
        verbose_name = "Class Timetable"
        verbose_name_plural = "Class Timetables"
        ordering = ["start_time"]


class ClassStudentRegistration(models.Model):
    STATE_OPTIONS = (
        (1, "Do"),
        (2, "Undo"),
        (3, "End"),
    )
    student = models.ForeignKey(Student, related_name="class_registrations", on_delete=models.CASCADE)
    class_model = models.ForeignKey(Class, related_name="student_registrations", on_delete=models.CASCADE)
    state = models.IntegerField(choices=STATE_OPTIONS, default=1)

    class Meta:
        unique_together = ("student", "class_model")


class StudentRegistration(models.Model):
    STATE_OPTIONS = (
        (1, "Do"),
        (2, "Undo"),
        (3, "End"),
    )
    student = models.ForeignKey(
        Student, related_name="registrations", on_delete=models.CASCADE
    )
    class_model = models.ForeignKey(
        Class, related_name="registrations", on_delete=models.CASCADE
    )
    state = models.IntegerField(choices=STATE_OPTIONS, default=1)


class ClassPayment(models.Model):
    date = models.DateField(verbose_name="Payment Date")
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Payment Amount"
    )
    student = models.ForeignKey(
        Student, related_name="class_payments", on_delete=models.CASCADE
    )
    class_model = models.ForeignKey(
        Class, related_name="payments", on_delete=models.CASCADE
    )


class Organ(models.Model):
    TYPE_OPTIONS = (
        ("language", "Language"),
        ("aboard", "Aboard"),
        ("industry", "Industry"),
        ("public", "Public"),
        ("hospital", "Hospital"),
        ("other", "Other"),
    )
    NATIONALITY_OPTIONS = (("uzbek", "Uzbek"), ("korean", "Korean"), ("other", "Other"))
    name_uz = models.CharField(max_length=100, verbose_name="Name (Uzbek)")
    name_ko = models.CharField(max_length=100, verbose_name="Name (Korean)")
    type = models.CharField(max_length=100, verbose_name="Type", choices=TYPE_OPTIONS)
    nationality = models.CharField(
        max_length=100, verbose_name="Nationality", choices=NATIONALITY_OPTIONS
    )
    representative_uz = models.CharField(max_length=100, blank=True, null=True)
    representative_ko = models.CharField(max_length=100, blank=True, null=True)
    position_uz = models.CharField(max_length=100, blank=True, null=True)
    position_ko = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(unique=True)
    contract_date = models.DateField(blank=True, null=True)
    agreement_date = models.DateField()
    logo = models.ImageField(
        upload_to="university_logos/",
        validators=[validate_image_size],
        blank=True,
        null=True,
    )


class UniversityManager(models.Model):
    university = models.ForeignKey(
        University, related_name="managers", on_delete=models.CASCADE
    )
    name_uz = models.CharField(max_length=100, verbose_name="Name (Uzbek)")
    name_ko = models.CharField(max_length=100, verbose_name="Name (Korean)")
    manager_id = models.IntegerField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=128, verbose_name="Password")
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="manager_profile",
    )

    class Meta:
        unique_together = ("university", "manager_id")
        verbose_name = "University Manager"
        verbose_name_plural = "University Managers"

    def save(self, *args, **kwargs):
        # Check if this is a new employee (no primary key yet)
        is_new = self.pk is None

        if is_new:
            # Hash the password before saving
            if self.password and not self.password.startswith("pbkdf2_"):
                self.password = make_password(self.password)

        super().save(*args, **kwargs)
        if is_new:
            user = User.objects.create(
                username=self.manager_id,
                first_name=self.name_ko or self.name_uz,
                password=self.password,
                is_active=True,
                is_staff=True,
            )

            university_staff_group, created = Group.objects.get_or_create(
                name="university_staff"
            )
            user.groups.add(university_staff_group)
            self.user = user
            super().save(update_fields=["user"])


class OrganManager(models.Model):
    organ = models.ForeignKey(Organ, related_name="manages", on_delete=models.CASCADE)
    name_uz = models.CharField(max_length=100, verbose_name="Name (Uzbek)")
    name_ko = models.CharField(max_length=100, verbose_name="Name (Korean)")
    manager_id = models.IntegerField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=128, verbose_name="Password")
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="organ_profile",
    )

    class Meta:
        unique_together = ("organ", "manager_id")
        verbose_name = "Organ Manager"
        verbose_name_plural = "Organ Managers"

    def save(self, *args, **kwargs):
        # Check if this is a new employee (no primary key yet)
        is_new = self.pk is None

        if is_new:
            # Hash the password before saving
            if self.password and not self.password.startswith("pbkdf2_"):
                self.password = make_password(self.password)

        super().save(*args, **kwargs)
        if is_new:
            user = User.objects.create(
                username=self.manager_id,
                first_name=self.name_ko or self.name_uz,
                password=self.password,
                is_active=True,
                is_staff=True,
            )

            organ_staff_group, created = Group.objects.get_or_create(name="organ_staff")
            user.groups.add(organ_staff_group)
            self.user = user
            super().save(update_fields=["user"])


class Career(models.Model):
    name_uz = models.CharField(max_length=100, verbose_name="Name (Uzbek)")
    name_ko = models.CharField(max_length=100, verbose_name="Name (Korean)")
    birth_date = models.DateField(verbose_name="Birth Date")
    gender = models.CharField(
        max_length=10,
        choices=(("male", "Male"), ("female", "Female")),
        verbose_name="Gender",
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Career"
        verbose_name_plural = "Careers"


class CareerHistory(models.Model):
    career = models.ForeignKey(Career, related_name="history", on_delete=models.CASCADE)
    work_title_uz = models.CharField(max_length=100, verbose_name="Work Title (Uzbek)")
    work_title_ko = models.CharField(max_length=100, verbose_name="Work Title (Korean)")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date", blank=True, null=True)
    region_uz = models.CharField(max_length=100, verbose_name="Region (Uzbek)")
    region_ko = models.CharField(max_length=100, verbose_name="Region (Korean)")
    visa = models.CharField(max_length=100, verbose_name="Visa", blank=True, null=True)


class CareerCounsel(models.Model):
    date = models.DateField(verbose_name="Counsel Date")
    details_uz = models.TextField(verbose_name="Details (Uzbek)", blank=True, null=True)
    details_ko = models.TextField(
        verbose_name="Details (Korean)", blank=True, null=True
    )
    career = models.ForeignKey(
        Career, related_name="counsels", on_delete=models.CASCADE
    )
