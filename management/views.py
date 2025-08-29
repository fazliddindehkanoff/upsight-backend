from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    EmployeeLoginSerializer,
    EmployeeSerializer,
    StudentSerializer,
    StudentDetailSerializer,
    EmployeeDetailSerializer,
    ClassSerializer,
    ClassDetailSerializer,
    ClassTimeTableSerializer,
    UniversitySerializer,
    UniversityDetailSerializer,
    EnteranceSerializer,
    OrganSerializer,
    CareerSerializer,
    EnterancePaymentSerializer,
    ClassPaymentSerializer,
    FinancePaymentSerializer,
)
from .models import (
    Student,
    Class,
    ClassTimeTable,
    ClassPayment,
    EnterancePayment,
    University,
    Enterance,
    Organ,
    Career,
    Employee,
)


def get_tokens_for_user(employee):
    """Generate JWT tokens for employee"""
    refresh = RefreshToken.for_user(employee.user)
    refresh["employee_id"] = employee.employee_id
    refresh["role"] = (
        employee.user.groups.first().name if employee.user.groups.first() else "user"
    )

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def employee_login(request):
    """
    Employee login endpoint that returns JWT token with employee information
    """
    serializer = EmployeeLoginSerializer(data=request.data)

    if serializer.is_valid():
        employee = serializer.validated_data["employee"]
        tokens = get_tokens_for_user(employee)

        # Serialize employee data
        employee_serializer = EmployeeSerializer(employee, context={"request": request})

        return Response(
            {
                "tokens": tokens,
                "user": employee_serializer.data,
                "message": "Login successful",
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {"error": "Invalid credentials", "details": serializer.errors},
        status=status.HTTP_401_UNAUTHORIZED,
    )


@api_view(["POST"])
def employee_logout(request):
    """
    Employee logout endpoint
    """
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
    except Exception:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def employee_profile(request):
    """
    Get current employee profile
    """
    try:
        # Get employee from user relationship
        employee = request.user.employee_profile
        serializer = EmployeeSerializer(employee, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except AttributeError:
        return Response(
            {"error": "Employee profile not found"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def students_list(request):
    """
    Get list of students based on user role.
    - upsight_staff: Can see all students
    - Others: Can see only the first student
    """
    try:
        # Check if user is in upsight_staff group
        is_upsight_staff = request.user.groups.filter(name="upsight_staff").exists()

        if is_upsight_staff:
            # Return all students for upsight staff
            students = Student.objects.all()
        else:
            # Return only first student for others
            students = Student.objects.all()[:1]

        serializer = StudentSerializer(
            students, many=True, context={"request": request}
        )

        return Response(
            {
                "students": serializer.data,
                "total_count": len(serializer.data),
                "access_level": "full" if is_upsight_staff else "limited",
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "Failed to fetch students", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def classes_list(request):
    """
    Get list of classes with their timetables
    """
    try:
        classes = Class.objects.all().prefetch_related("timetables")
        serializer = ClassSerializer(classes, many=True, context={"request": request})

        return Response(
            {
                "classes": serializer.data,
                "total_count": len(serializer.data),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "Failed to fetch classes", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def class_detail(request, class_id):
    """
    Get a specific class with its timetables, payments, and student registrations.
    Supports filtering payments by month using ?month=X query parameter.
    """
    try:
        # Get month filter from query parameters
        month_filter = request.GET.get("month")
        if month_filter:
            try:
                month_filter = int(month_filter)
                if month_filter < 1:
                    return Response(
                        {"error": "Month must be a positive integer"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except ValueError:
                return Response(
                    {"error": "Month must be a valid integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Fetch class with related data
        class_obj = Class.objects.prefetch_related(
            "timetables", "payments__student", "student_registrations__student"
        ).get(id=class_id)
        # Create serializer context with month filter
        context = {"request": request}
        if month_filter:
            context["month_filter"] = month_filter

        serializer = ClassDetailSerializer(class_obj, context=context)

        response_data = serializer.data

        # Add filter info to response
        if month_filter:
            response_data["filter_info"] = {
                "filtered_by_month": month_filter,
                "class_current_month": class_obj.current_month,
            }

        return Response(response_data, status=status.HTTP_200_OK)

    except Class.DoesNotExist:
        return Response({"error": "Class not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "Failed to fetch class", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def class_timetables(request, class_id):
    """
    Get timetables for a specific class
    """
    try:
        timetables = ClassTimeTable.objects.filter(class_model_id=class_id)
        serializer = ClassTimeTableSerializer(
            timetables, many=True, context={"request": request}
        )

        return Response(
            {
                "timetables": serializer.data,
                "class_id": class_id,
                "total_count": len(serializer.data),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "Failed to fetch timetables", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# University Views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def universities_list(request):
    """Get list of universities for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view universities."},
                status=status.HTTP_403_FORBIDDEN,
            )

        universities = University.objects.all()
        serializer = UniversitySerializer(
            universities, many=True, context={"request": request}
        )

        return Response(
            {
                "universities": serializer.data,
                "total_count": len(serializer.data),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "Failed to fetch universities", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def university_detail(request, university_id):
    """Get university details for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view university details."},
                status=status.HTTP_403_FORBIDDEN,
            )

        university = University.objects.get(id=university_id)
        serializer = UniversityDetailSerializer(
            university, context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    except University.DoesNotExist:
        return Response(
            {"error": "University not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to fetch university", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Employee Views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def employees_list(request):
    """Get list of employees for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view employees."},
                status=status.HTTP_403_FORBIDDEN,
            )

        employees = Employee.objects.all()
        serializer = EmployeeSerializer(
            employees, many=True, context={"request": request}
        )

        return Response(
            {
                "employees": serializer.data,
                "total_count": len(serializer.data),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "Failed to fetch employees", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def employee_detail(request, employee_id):
    """Get employee details for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view employee details."},
                status=status.HTTP_403_FORBIDDEN,
            )

        employee = Employee.objects.prefetch_related("attached_documents").get(
            id=employee_id
        )
        serializer = EmployeeDetailSerializer(employee, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Employee.DoesNotExist:
        return Response(
            {"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to fetch employee", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Enhanced Student Views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_detail(request, student_id):
    """Get student details for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view student details."},
                status=status.HTTP_403_FORBIDDEN,
            )

        student = Student.objects.prefetch_related("attached_documents").get(
            id=student_id
        )
        serializer = StudentDetailSerializer(student, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Student.DoesNotExist:
        return Response(
            {"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to fetch student", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Enterance Views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def enterances_list(request):
    """Get list of enterances for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view enterances."},
                status=status.HTTP_403_FORBIDDEN,
            )

        enterances = Enterance.objects.select_related("university").all()
        serializer = EnteranceSerializer(
            enterances, many=True, context={"request": request}
        )

        return Response(
            {
                "enterances": serializer.data,
                "total_count": len(serializer.data),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "Failed to fetch enterances", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def enterance_detail(request, enterance_id):
    """Get enterance details for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view enterance details."},
                status=status.HTTP_403_FORBIDDEN,
            )

        enterance = Enterance.objects.select_related("university").get(id=enterance_id)
        serializer = EnteranceSerializer(enterance, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Enterance.DoesNotExist:
        return Response(
            {"error": "Enterance not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to fetch enterance", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Organ Views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def organs_list(request):
    """Get list of organs for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view organs."},
                status=status.HTTP_403_FORBIDDEN,
            )

        organs = Organ.objects.all()
        serializer = OrganSerializer(organs, many=True, context={"request": request})

        return Response(
            {
                "organs": serializer.data,
                "total_count": len(serializer.data),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "Failed to fetch organs", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def organ_detail(request, organ_id):
    """Get organ details for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view organ details."},
                status=status.HTTP_403_FORBIDDEN,
            )

        organ = Organ.objects.get(id=organ_id)
        serializer = OrganSerializer(organ, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Organ.DoesNotExist:
        return Response({"error": "Organ not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "Failed to fetch organ", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Career Views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def careers_list(request):
    """Get list of careers for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view careers."},
                status=status.HTTP_403_FORBIDDEN,
            )

        careers = Career.objects.prefetch_related("history", "counsels").all()
        serializer = CareerSerializer(careers, many=True, context={"request": request})

        return Response(
            {
                "careers": serializer.data,
                "total_count": len(serializer.data),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "Failed to fetch careers", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Finance Views
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def finance_payments_list(request):
    """
    Get combined list of all payments (entrance and class payments) for upsight_staff
    """
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view payment data."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get all entrance payments
        entrance_payments = EnterancePayment.objects.select_related(
            "student", "enterance__university"
        ).all()
        
        # Get all class payments
        class_payments = ClassPayment.objects.select_related(
            "student", "class_model"
        ).all()

        # Convert to unified format
        payments_data = []
        
        # Add entrance payments
        for payment in entrance_payments:
            payments_data.append({
                'id': f"entrance_{payment.id}",
                'original_id': payment.id,
                'date': payment.date,
                'amount': payment.amount,
                'payment_type': 'entrance',
                'student_id': payment.student.student_id,
                'student_name_ko': payment.student.name_ko,
                'student_name_uz': payment.student.name_uz,
                'university_name': str(payment.enterance.university),
                'enterance_info': (
                    f"{payment.enterance.years} - {payment.enterance.get_kind_display()} "
                    f"({payment.enterance.get_order_display()})"
                ),
                'payment_month': None,
                'payment_month_display': None,
                'class_info': None,
            })
        
        # Add class payments
        for payment in class_payments:
            payments_data.append({
                'id': f"class_{payment.id}",
                'original_id': payment.id,
                'date': payment.date,
                'amount': payment.amount,
                'payment_type': 'class',
                'student_id': payment.student.student_id,
                'student_name_ko': payment.student.name_ko,
                'student_name_uz': payment.student.name_uz,
                'university_name': None,
                'enterance_info': None,
                'payment_month': payment.payment_month,
                'payment_month_display': f"Month {payment.payment_month}",
                'class_info': (
                    f"Group {payment.class_model.group} - {payment.class_model.get_level_display()} "
                    f"{payment.class_model.get_lecture_display()}"
                ),
            })

        # Sort by date (most recent first)
        payments_data.sort(key=lambda x: x['date'], reverse=True)

        # Serialize the data
        serializer = FinancePaymentSerializer(payments_data, many=True)

        # Calculate totals
        total_amount = sum(float(payment['amount']) for payment in payments_data)
        entrance_total = sum(
            float(payment['amount']) for payment in payments_data
            if payment['payment_type'] == 'entrance'
        )
        class_total = sum(
            float(payment['amount']) for payment in payments_data
            if payment['payment_type'] == 'class'
        )

        return Response(
            {
                "payments": serializer.data,
                "total_count": len(payments_data),
                "totals": {
                    "total_amount": total_amount,
                    "entrance_payments_total": entrance_total,
                    "class_payments_total": class_total,
                    "entrance_payments_count": len([p for p in payments_data if p['payment_type'] == 'entrance']),
                    "class_payments_count": len([p for p in payments_data if p['payment_type'] == 'class']),
                }
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "Failed to fetch payments", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def entrance_payments_list(request):
    """Get list of entrance payments for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view entrance payments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        payments = EnterancePayment.objects.select_related(
            "student", "enterance__university"
        ).all().order_by('-date')
        
        serializer = EnterancePaymentSerializer(payments, many=True, context={"request": request})

        return Response(
            {
                "entrance_payments": serializer.data,
                "total_count": len(serializer.data),
                "total_amount": sum(payment.amount for payment in payments),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "Failed to fetch entrance payments", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def class_payments_list(request):
    """Get list of class payments for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view class payments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        payments = ClassPayment.objects.select_related("student", "class_model").all().order_by('-date')
        
        serializer = ClassPaymentSerializer(payments, many=True, context={"request": request})

        return Response(
            {
                "class_payments": serializer.data,
                "total_count": len(serializer.data),
                "total_amount": sum(payment.amount for payment in payments),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "Failed to fetch class payments", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def entrance_payment_detail(request, payment_id):
    """Get entrance payment details for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view entrance payment details."},
                status=status.HTTP_403_FORBIDDEN,
            )

        payment = EnterancePayment.objects.select_related(
            "student", "enterance__university"
        ).get(id=payment_id)
        
        serializer = EnterancePaymentSerializer(payment, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    except EnterancePayment.DoesNotExist:
        return Response(
            {"error": "Entrance payment not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to fetch entrance payment", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def class_payment_detail(request, payment_id):
    """Get class payment details for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view class payment details."},
                status=status.HTTP_403_FORBIDDEN,
            )

        payment = ClassPayment.objects.select_related("student", "class_model").get(id=payment_id)
        
        serializer = ClassPaymentSerializer(payment, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    except ClassPayment.DoesNotExist:
        return Response(
            {"error": "Class payment not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to fetch class payment", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def career_detail(request, career_id):
    """Get career details for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view career details."},
                status=status.HTTP_403_FORBIDDEN,
            )

        career = Career.objects.prefetch_related("history", "counsels").get(
            id=career_id
        )
        serializer = CareerSerializer(career, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Career.DoesNotExist:
        return Response({"error": "Career not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": "Failed to fetch career", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
