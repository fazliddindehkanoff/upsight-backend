from rest_framework import serializers
from django.db import models
from django.contrib.auth.hashers import check_password
from .models import (
    Employee,
    Student,
    Class,
    ClassTimeTable,
    University,
    Enterance,
    AttachedDocument,
    EmployeeDocument,
    StudentRegistration,
    Organ,
    Career,
    CareerHistory,
    CareerCounsel,
)


class EmployeeLoginSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        employee_id = attrs.get("employee_id")
        password = attrs.get("password")

        if employee_id and password:
            try:
                employee = Employee.objects.get(employee_id=employee_id)
                if check_password(password, employee.password):
                    attrs["employee"] = employee
                    return attrs
            except Employee.DoesNotExist:
                pass

        raise serializers.ValidationError("Invalid credentials.")


class EmployeeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ["id", "employee_id", "email", "name", "role", "avatar"]

    def get_name(self, obj):
        return obj.name_ko or obj.name_uz

    def get_role(self, obj):
        return "upsight_staff"

    def get_avatar(self, obj):
        if obj.picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.picture.url)
        return "/placeholder.svg?height=40&width=40"


class StudentSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    guardian_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    enterance_payment_amount = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "student_id",
            "name",
            "birth_date",
            "gender",
            "telephone",
            "address",
            "email",
            "avatar",
            "high_school",
            "college",
            "university",
            "master",
            "other_education",
            "guardian_name",
            "guardian_telephone",
            "guardian_relationship",
            "created_at",
            "enterance_payment_amount"
        ]

    def get_name(self, obj):
        return obj.name_ko or obj.name_uz

    def get_guardian_name(self, obj):
        return obj.guardian_name_ko or obj.guardian_name_uz

    def get_avatar(self, obj):
        if obj.picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.picture.url)
        return "/placeholder.svg?height=40&width=40"

    def get_enterance_payment_amount(self, obj):
        if hasattr(obj, "enterance_payment_amount"):
            return obj.enterance_payment_amount
        return 0


class ClassTimeTableSerializer(serializers.ModelSerializer):
    days_display = serializers.SerializerMethodField()
    days_display_ko = serializers.SerializerMethodField()
    days_display_uz = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = ClassTimeTable
        fields = [
            "id",
            "days",
            "days_display",
            "days_display_ko",
            "days_display_uz",
            "start_time",
            "end_time",
            "duration",
            "created_at",
        ]

    def get_days_display(self, obj):
        """Get bilingual display names for all selected days"""
        return obj.get_days_display()

    def get_days_display_ko(self, obj):
        """Get Korean day names"""
        return obj.get_days_display_ko()

    def get_days_display_uz(self, obj):
        """Get Uzbek day names"""
        return obj.get_days_display_uz()

    def get_duration(self, obj):
        """Calculate duration between start and end time"""
        if obj.start_time and obj.end_time:
            start = obj.start_time
            end = obj.end_time
            duration = (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)
            hours = duration // 60
            minutes = duration % 60
            return f"{hours}h {minutes}m"
        return "0h 0m"


class ClassSerializer(serializers.ModelSerializer):
    teacher_first_name = serializers.CharField(
        source="teacher_first.get_name", read_only=True
    )
    teacher_second_name = serializers.CharField(
        source="teacher_second.get_name", read_only=True
    )
    level_display = serializers.CharField(source="get_level_display", read_only=True)
    lecture_display = serializers.CharField(
        source="get_lecture_display", read_only=True
    )
    timetables = ClassTimeTableSerializer(many=True, read_only=True)

    class Meta:
        model = Class
        fields = [
            "id",
            "teacher_first",
            "teacher_first_name",
            "teacher_second",
            "teacher_second_name",
            "level",
            "level_display",
            "lecture",
            "lecture_display",
            "group",
            "opening_date",
            "period",
            "tuition_fee",
            "textbook_first",
            "textbook_second",
            "classroom",
            "timetables",
        ]


class ClassTimeTableCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTimeTable
        fields = ["id", "class_model", "days", "start_time", "end_time"]

    def validate(self, data):
        """Validate that end_time is after start_time and days are valid"""
        if data.get("start_time") and data.get("end_time"):
            if data["start_time"] >= data["end_time"]:
                raise serializers.ValidationError("End time must be after start time.")

        # Validate days
        valid_days = [choice[0] for choice in ClassTimeTable.WEEKDAY_CHOICES]
        days = data.get("days", [])

        if not isinstance(days, list):
            raise serializers.ValidationError("Days must be a list of day values.")

        for day in days:
            if day not in valid_days:
                raise serializers.ValidationError(
                    f"Invalid day: {day}. Valid options are: {valid_days}"
                )

        return data


class UniversitySerializer(serializers.ModelSerializer):
    representative_name = serializers.SerializerMethodField()
    contract_display = serializers.CharField(
        source="get_contract_display", read_only=True
    )
    grade_display = serializers.CharField(source="get_grade_display", read_only=True)
    years_display = serializers.CharField(source="get_years_display", read_only=True)

    class Meta:
        model = University
        fields = [
            "id",
            "name_ko",
            "name_uz",
            "grade",
            "grade_display",
            "years",
            "years_display",
            "representative_uz",
            "representative_ko",
            "representative_name",
            "position_uz",
            "position_ko",
            "phone",
            "telephone",
            "address",
            "email",
            "contract",
            "contract_display",
            "agreement_date",
            "logo",
        ]

    def get_representative_name(self, obj):
        return f"{obj.representative_ko or ''} / {obj.representative_uz or ''}".strip(
            " /"
        )


class EnteranceSerializer(serializers.ModelSerializer):
    university_name = serializers.CharField(source="university.__str__", read_only=True)
    kind_display = serializers.CharField(source="get_kind_display", read_only=True)
    order_display = serializers.CharField(source="get_order_display", read_only=True)
    state_display = serializers.CharField(source="get_state_display", read_only=True)
    students = serializers.SerializerMethodField()

    class Meta:
        model = Enterance
        fields = [
            "id",
            "university",
            "university_name",
            "years",
            "kind",
            "kind_display",
            "order",
            "order_display",
            "from_date",
            "to_date",
            "contract_no",
            "state",
            "state_display",
            "students",
        ]

    def get_students(self, obj):
        registrations = obj.student_registrations.select_related("student")
        students = []
        for reg in registrations:
            student = reg.student
            payment_amounts = student.payments.all()
            payment_amount = 0
            for payment in payment_amounts:
                print(payment.enterance)
                if payment.enterance == obj:
                    payment_amount += payment.amount
            student.enterance_payment_amount = payment_amount
            students.append(student)
        return StudentSerializer(students, many=True, context=self.context).data


class AttachedDocumentSerializer(serializers.ModelSerializer):
    document_name = serializers.SerializerMethodField()

    class Meta:
        model = AttachedDocument
        fields = [
            "id",
            "document_name_ko",
            "document_name_uz",
            "document_name",
            "file",
            "uploaded_at",
        ]

    def get_document_name(self, obj):
        return obj.document_name_ko or obj.document_name_uz


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    document_name = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeDocument
        fields = [
            "id",
            "document_name_ko",
            "document_name_uz",
            "document_name",
            "file",
            "uploaded_at",
        ]

    def get_document_name(self, obj):
        return obj.document_name_ko or obj.document_name_uz


class StudentDetailSerializer(StudentSerializer):
    attached_documents = AttachedDocumentSerializer(many=True, read_only=True)

    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields + ["attached_documents"]


class EmployeeDetailSerializer(EmployeeSerializer):
    attached_documents = EmployeeDocumentSerializer(many=True, read_only=True)

    class Meta(EmployeeSerializer.Meta):
        fields = EmployeeSerializer.Meta.fields + [
            "attached_documents",
            "salary",
            "bonus",
            "status",
        ]


class OrganSerializer(serializers.ModelSerializer):
    representative_name = serializers.SerializerMethodField()
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    nationality_display = serializers.CharField(
        source="get_nationality_display", read_only=True
    )

    class Meta:
        model = Organ
        fields = [
            "id",
            "name_uz",
            "name_ko",
            "type",
            "type_display",
            "nationality",
            "nationality_display",
            "representative_uz",
            "representative_ko",
            "representative_name",
            "position_uz",
            "position_ko",
            "phone",
            "telephone",
            "address",
            "email",
            "contract_date",
            "agreement_date",
            "logo",
        ]

    def get_representative_name(self, obj):
        return f"{obj.representative_ko or ''} / {obj.representative_uz or ''}".strip(
            " /"
        )


class CareerHistorySerializer(serializers.ModelSerializer):
    work_title = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()

    class Meta:
        model = CareerHistory
        fields = [
            "id",
            "work_title_uz",
            "work_title_ko",
            "work_title",
            "start_date",
            "end_date",
            "region_uz",
            "region_ko",
            "region",
            "visa",
        ]

    def get_work_title(self, obj):
        return obj.work_title_ko or obj.work_title_uz

    def get_region(self, obj):
        return obj.region_ko or obj.region_uz


class CareerCounselSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()

    class Meta:
        model = CareerCounsel
        fields = ["id", "date", "details_uz", "details_ko", "details"]

    def get_details(self, obj):
        return obj.details_ko or obj.details_uz


class CareerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    gender_display = serializers.CharField(source="get_gender_display", read_only=True)
    history = CareerHistorySerializer(many=True, read_only=True)
    counsels = CareerCounselSerializer(many=True, read_only=True)

    class Meta:
        model = Career
        fields = [
            "id",
            "name_uz",
            "name_ko",
            "name",
            "birth_date",
            "gender",
            "gender_display",
            "phone_number",
            "telephone",
            "history",
            "counsels",
        ]

    def get_name(self, obj):
        return obj.name_ko or obj.name_uz


class StudentRegistrationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.__str__", read_only=True)
    class_info = serializers.SerializerMethodField()
    state_display = serializers.CharField(source="get_state_display", read_only=True)

    class Meta:
        model = StudentRegistration
        fields = [
            "id",
            "student",
            "student_name",
            "class_model",
            "class_info",
            "state",
            "state_display",
        ]

    def get_class_info(self, obj):
        return (
            f"Group {obj.class_model.group} - {obj.class_model.get_level_display()} "
            f"{obj.class_model.get_lecture_display()}"
        )
