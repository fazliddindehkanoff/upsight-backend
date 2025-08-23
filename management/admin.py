from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline

from .models import (
    Student,
    AttachedDocument,
    Employee,
    EmployeeDocument,
    University,
    UniversityManager,
    Enterance,
    EnteranceDocument,
    EnteranceStudentRegistration,
    Class,
    ClassTimeTable,
    ClassStudentRegistration,
    Organ,
    OrganManager,
    Career,
    CareerCounsel,
    CareerHistory,
    ClassPayment,
    EnterancePayment
)


class CareerHistoryInline(TabularInline):
    model = CareerHistory
    extra = 1  # Allow adding one extra history by default
    fields = (
        "work_title_uz",
        "work_title_ko",
        "start_date",
        "end_date",
        "region_uz",
        "region_ko",
        "visa",
    )


class CareerCounselInline(TabularInline):
    model = CareerCounsel
    extra = 1  # Allow adding one extra counsel by default
    fields = ("date", "details_uz", "details_ko")


class OrganManagerInline(TabularInline):
    model = OrganManager
    extra = 1  # Allow adding one extra manager by default
    fields = ("name_ko", "name_uz", "manager_id", "password", "phone_number", "user")
    readonly_fields = ("user",)


class EnteranceStudentRegistrationInline(TabularInline):
    model = EnteranceStudentRegistration
    extra = 1  # Allow adding one extra registration by default
    fields = ("student", "date", "contract", "bonus", "state", "recommend")


class ClassStudentRegistrationInline(TabularInline):
    model = ClassStudentRegistration
    extra = 1  # Allow adding one extra registration by default
    fields = ("student", "class_model", "state")


class EnteranceDocumentInline(TabularInline):
    model = EnteranceDocument
    extra = 1  # Allow adding one extra document by default
    fields = ("document_name_ko", "document_name_uz", "file", "uploaded_at")
    readonly_fields = ("uploaded_at",)


class AttachedDocumentInline(TabularInline):
    model = AttachedDocument
    extra = 1  # Allow adding one extra document by default
    fields = ("document_name_ko", "document_name_uz", "file", "uploaded_at")
    readonly_fields = ("uploaded_at",)


class EmployeeDocumentInline(TabularInline):
    model = EmployeeDocument
    extra = 1  # Allow adding one extra document by default
    fields = ("document_name_ko", "document_name_uz", "file", "uploaded_at")
    readonly_fields = ("uploaded_at",)


class UniversityManagerInline(TabularInline):
    model = UniversityManager
    extra = 1  # Allow adding one extra manager by default
    fields = ("name_ko", "name_uz", "manager_id", "password", "phone_number", "user")
    readonly_fields = ("user",)


class ClassTimeTableInline(TabularInline):
    model = ClassTimeTable
    extra = 1
    fields = ("days", "start_time", "end_time")
    ordering = ["start_time"]


@admin.register(Organ)
class OrganAdmin(ModelAdmin):
    list_display = [
        "name_ko",
        "name_uz",
        "type",
        "representative_uz",
        "representative_ko",
        "contract_date",
        "phone",
    ]
    inlines = [OrganManagerInline]
    search_fields = ["name_ko", "name_uz", "representative_uz", "representative_ko"]


@admin.register(Enterance)
class EnteranceAdmin(ModelAdmin):
    list_display = ["years", "kind", "order", "from_date", "to_date"]
    inlines = [EnteranceDocumentInline, EnteranceStudentRegistrationInline]


@admin.register(University)
class UniversityAdmin(ModelAdmin):
    list_display = [
        "name_uz",
        "name_ko",
        "grade",
        "years",
        "representative_uz",
        "telephone",
        "position_uz",
    ]

    inlines = [UniversityManagerInline]

    def get_name_display(self, obj):
        return f"{obj.name_ko} / {obj.name_uz}"

    get_name_display.short_description = "Name (KO/UZ)"


@admin.register(ClassPayment)
class ClassPaymentAdmin(ModelAdmin):
    pass


@admin.register(EnterancePayment)
class EnterancePaymentAdmin(ModelAdmin):
    pass


@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = [
        "get_name_display",
        "employee_id",
        "position",
        "email",
        "telephone",
        "status",
        "user",
        "created_at",
    ]
    list_filter = [
        "gender",
        "position",
        "status",
        "birth_date",
        "start_date",
        "created_at",
    ]
    search_fields = [
        "name_ko",
        "name_uz",
        "employee_id",
        "email",
        "telephone",
        "user__username",
    ]
    readonly_fields = ["created_at", "updated_at", "user"]

    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    ("name_ko", "name_uz"),
                    "birth_date",
                    "gender",
                    "start_date",
                    "telephone",
                    "address",
                    "email",
                    "picture",
                )
            },
        ),
        (
            "Education Background",
            {
                "fields": (
                    "college",
                    "university",
                    "graduate",
                ),
            },
        ),
        (
            "Employment Details",
            {
                "fields": (
                    "position",
                    "salary",
                    "bonus",
                    "status",
                )
            },
        ),
        ("Authentication", {"fields": ("employee_id", "password", "user")}),
    )

    inlines = [EmployeeDocumentInline]

    def get_name_display(self, obj):
        return f"{obj.name_ko} / {obj.name_uz}"

    get_name_display.short_description = "Name (KO/UZ)"


@admin.register(Student)
class StudentAdmin(ModelAdmin):
    list_display = [
        "get_name_display",
        "student_id",
        "email",
        "telephone",
        "created_at",
    ]
    list_filter = ["gender", "guardian_relationship", "birth_date", "created_at"]
    search_fields = ["name_ko", "name_uz", "student_id", "email", "telephone"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    ("name_ko", "name_uz"),
                    ("birth_date"),
                    "gender",
                    "telephone",
                    "address",
                    "email",
                    "picture",
                )
            },
        ),
        (
            "Education Background",
            {
                "fields": (
                    "high_school",
                    "college",
                    "university",
                    "master",
                    "other_education",
                ),
            },
        ),
        (
            "Guardian Information",
            {
                "fields": (
                    ("guardian_name_ko", "guardian_name_uz"),
                    "guardian_telephone",
                    "guardian_relationship",
                )
            },
        ),
        ("Authentication", {"fields": ("student_id", "password")}),
    )

    inlines = [AttachedDocumentInline]

    def get_name_display(self, obj):
        return f"{obj.name_ko} / {obj.name_uz}"

    get_name_display.short_description = "Name (KO/UZ)"


@admin.register(Class)
class ClassAdmin(ModelAdmin):
    list_display = [
        "get_class_info",
        "level",
        "lecture",
        "group",
        "opening_date",
        "period",
        "tuition_fee",
    ]
    list_filter = ["level", "lecture", "group", "opening_date"]
    search_fields = ["teacher_first__name_ko", "teacher_second__name_ko", "classroom"]

    fieldsets = (
        (
            "Teachers",
            {
                "fields": (
                    "teacher_first",
                    "teacher_second",
                )
            },
        ),
        (
            "Class Details",
            {
                "fields": (
                    "level",
                    "lecture",
                    "group",
                    "opening_date",
                    "period",
                    "tuition_fee",
                )
            },
        ),
        (
            "Resources",
            {
                "fields": (
                    "textbook_first",
                    "textbook_second",
                    "classroom",
                )
            },
        ),
    )

    inlines = [ClassTimeTableInline, ClassStudentRegistrationInline]

    def get_class_info(self, obj):
        return (
            f"Group {obj.group} - {obj.get_level_display()} {obj.get_lecture_display()}"
        )

    get_class_info.short_description = "Class Info"


@admin.register(ClassTimeTable)
class ClassTimeTableAdmin(ModelAdmin):
    list_display = [
        "class_model",
        "get_days_display_short",
        "start_time",
        "end_time",
        "get_duration",
    ]
    list_filter = ["class_model__level", "class_model__lecture", "start_time"]
    search_fields = [
        "class_model__teacher_first__name_ko",
        "class_model__teacher_second__name_ko",
    ]
    ordering = ["class_model", "start_time"]

    fields = (
        "class_model",
        "days",
        ("start_time", "end_time"),
        ("created_at", "updated_at"),
    )
    readonly_fields = ("created_at", "updated_at")

    def get_days_display_short(self, obj):
        """Get short display of selected days"""
        days_display = obj.get_days_display()
        if len(days_display) > 3:
            return f"{', '.join(days_display[:3])}... (+{len(days_display)-3})"
        return ", ".join(days_display) if days_display else "No days"

    get_days_display_short.short_description = "Days"

    def get_duration(self, obj):
        if obj.start_time and obj.end_time:
            start = obj.start_time
            end = obj.end_time
            duration = (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)
            hours = duration // 60
            minutes = duration % 60
            return f"{hours}h {minutes}m"
        return "-"

    get_duration.short_description = "Duration"


@admin.register(Career)
class CareerAdmin(ModelAdmin):
    list_display = [
        "get_name_display",
        "birth_date",
        "gender",
        "phone_number",
        "telephone",
    ]
    list_filter = ["gender", "birth_date"]
    search_fields = ["name_ko", "name_uz", "phone_number", "telephone"]

    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    ("name_ko", "name_uz"),
                    "birth_date",
                    "gender",
                    ("phone_number", "telephone"),
                )
            },
        ),
    )

    inlines = [CareerHistoryInline, CareerCounselInline]

    def get_name_display(self, obj):
        return f"{obj.name_ko} / {obj.name_uz}"

    get_name_display.short_description = "Name (KO/UZ)"
