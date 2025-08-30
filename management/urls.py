from django.urls import path
from .views import (
    unified_login,
    employee_logout,
    employee_profile,
    students_list,
    student_detail,
    employees_list,
    employee_detail,
    classes_list,
    class_detail,
    class_timetables,
    universities_list,
    university_detail,
    enterances_list,
    enterance_detail,
    organs_list,
    organ_detail,
    careers_list,
    career_detail,
    finance_payments_list,
    entrance_payments_list,
    class_payments_list,
    entrance_payment_detail,
    class_payment_detail,
)

urlpatterns = [
    # Authentication endpoints
    # path("auth/login", employee_login, name="employee_login"),
    path("auth/login", unified_login, name="unified_login"),
    path("auth/logout", employee_logout, name="employee_logout"),
    path("auth/profile", employee_profile, name="employee_profile"),
    # Student endpoints
    path("students", students_list, name="students_list"),
    path("students/<int:student_id>", student_detail, name="student_detail"),
    # Employee endpoints
    path("employees", employees_list, name="employees_list"),
    path("employees/<int:employee_id>", employee_detail, name="employee_detail"),
    # Class endpoints
    path("classes", classes_list, name="classes_list"),
    path("classes/<int:class_id>", class_detail, name="class_detail"),
    path(
        "classes/<int:class_id>/timetables", class_timetables, name="class_timetables"
    ),
    # University endpoints
    path("universities", universities_list, name="universities_list"),
    path(
        "universities/<int:university_id>", university_detail, name="university_detail"
    ),
    # Enterance endpoints
    path("enterances", enterances_list, name="enterances_list"),
    path("enterances/<int:enterance_id>", enterance_detail, name="enterance_detail"),
    # Organ endpoints
    path("organs", organs_list, name="organs_list"),
    path("organs/<int:organ_id>", organ_detail, name="organ_detail"),
    # Career endpoints
    path("careers", careers_list, name="careers_list"),
    path("careers/<int:career_id>", career_detail, name="career_detail"),
    # Finance endpoints
    path("finance/payments", finance_payments_list, name="finance_payments_list"),
    path("finance/entrance-payments", entrance_payments_list, name="entrance_payments_list"),
    path("finance/class-payments", class_payments_list, name="class_payments_list"),
    path("finance/entrance-payments/<int:payment_id>", entrance_payment_detail, name="entrance_payment_detail"),
    path("finance/class-payments/<int:payment_id>", class_payment_detail, name="class_payment_detail"),
]
