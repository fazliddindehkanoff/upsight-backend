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
    ClassTimeTableSerializer,
    ClassTimeTableCreateUpdateSerializer,
    UniversitySerializer,
    EnteranceSerializer,
    OrganSerializer,
    CareerSerializer,
)
from .models import (
    Student, Class, ClassTimeTable, University, Enterance,
    Organ, Career, Employee
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
    Get a specific class with its timetables
    """
    try:
        class_obj = Class.objects.prefetch_related("timetables").get(id=class_id)
        serializer = ClassSerializer(class_obj, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

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
                status=status.HTTP_403_FORBIDDEN
            )
        
        universities = University.objects.all()
        serializer = UniversitySerializer(universities, many=True, context={"request": request})
        
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
                status=status.HTTP_403_FORBIDDEN
            )
        
        university = University.objects.get(id=university_id)
        serializer = UniversitySerializer(university, context={"request": request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except University.DoesNotExist:
        return Response(
            {"error": "University not found"},
            status=status.HTTP_404_NOT_FOUND
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
                status=status.HTTP_403_FORBIDDEN
            )
        
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True, context={"request": request})
        
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
                status=status.HTTP_403_FORBIDDEN
            )
        
        employee = Employee.objects.prefetch_related('attached_documents').get(id=employee_id)
        serializer = EmployeeDetailSerializer(employee, context={"request": request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Employee.DoesNotExist:
        return Response(
            {"error": "Employee not found"},
            status=status.HTTP_404_NOT_FOUND
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
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = Student.objects.prefetch_related('attached_documents').get(id=student_id)
        serializer = StudentDetailSerializer(student, context={"request": request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Student.DoesNotExist:
        return Response(
            {"error": "Student not found"},
            status=status.HTTP_404_NOT_FOUND
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
                status=status.HTTP_403_FORBIDDEN
            )
        
        enterances = Enterance.objects.select_related('university').all()
        serializer = EnteranceSerializer(enterances, many=True, context={"request": request})
        
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
                status=status.HTTP_403_FORBIDDEN
            )
        
        enterance = Enterance.objects.select_related('university').get(id=enterance_id)
        serializer = EnteranceSerializer(enterance, context={"request": request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Enterance.DoesNotExist:
        return Response(
            {"error": "Enterance not found"},
            status=status.HTTP_404_NOT_FOUND
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
                status=status.HTTP_403_FORBIDDEN
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
                status=status.HTTP_403_FORBIDDEN
            )
        
        organ = Organ.objects.get(id=organ_id)
        serializer = OrganSerializer(organ, context={"request": request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Organ.DoesNotExist:
        return Response(
            {"error": "Organ not found"},
            status=status.HTTP_404_NOT_FOUND
        )
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
                status=status.HTTP_403_FORBIDDEN
            )
        
        careers = Career.objects.prefetch_related('history', 'counsels').all()
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def career_detail(request, career_id):
    """Get career details for upsight_staff"""
    try:
        if not request.user.groups.filter(name="upsight_staff").exists():
            return Response(
                {"error": "Permission denied. Only staff can view career details."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        career = Career.objects.prefetch_related('history', 'counsels').get(id=career_id)
        serializer = CareerSerializer(career, context={"request": request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Career.DoesNotExist:
        return Response(
            {"error": "Career not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": "Failed to fetch career", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
