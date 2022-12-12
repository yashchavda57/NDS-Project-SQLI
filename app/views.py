from django.shortcuts import render, redirect
from app.models import Employee, Blog
from app.forms import BlogForm
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import connection
import subprocess, shlex
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):
    return render(request, "app/index.html")

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(request, "New user created! Please sign in.")
            return redirect('app:index')
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form":form})

@login_required
def home(request):
    return render(request, "app/home.html")

@login_required
def employees(request):
    if request.method == "POST":
        emp_id = request.POST.get("emp_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        age = request.POST.get("age")
        sex = request.POST.get("sex")
        department = request.POST.get("department")
        designation = request.POST.get("designation")

        # Saving to DB using Django ORM - the best way
        Employee.objects.create(emp_id=emp_id, first_name=first_name, last_name=last_name,
        age=age, sex=sex, department=department, designation=designation)

        # # Direct SQL Queries - the wrong way
        # cursor = connection.cursor()
        # query = "INSERT INTO app_employee (emp_id, first_name, last_name, age, sex, department, designation) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (emp_id, first_name, last_name, age, sex, department, designation)
        # cursor.execute(query)

        # # Direct SQL Queries - the correct way
        # cursor = connection.cursor()
        # cursor.execute("INSERT INTO app_employee (emp_id, first_name, last_name, age, sex, department, designation) VALUES (%s, %s, %s, %s, %s, %s, %s)", [emp_id, first_name, last_name, age, sex, department, designation])

        return redirect("app:employees")
    else:
        # Fetch all employees using Django ORM
        employees = Employee.objects.all()

        return render(request, 'app/employees.html',
        {"employees":employees})
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_requiredp
@csrf_exempt
def search_employees(request):
    if is_ajax(request=request):
        search_term = request.POST.get('searchTerm')

        # Searching employees using Django ORM - the best way
        # employees = Employee.objects.filter(first_name__icontains=search_term)

        # # Searching employees using raw() - the wrong way
        query = "SELECT * FROM app_employee WHERE first_name ILIKE '%s';" % search_term
        employees = Employee.objects.raw(query)

        # # Searching employees using raw() - the correct way
        # employees = Employee.objects.raw('SELECT * FROM app_employee WHERE first_name ILIKE %s;',[search_term])

        # # Searching employees using extra() - the wrong way
        # employees = Employee.objects.extra(where=["first_name ILIKE '%s'" % search_term])

        # # Searching employees using extra() - the correct way
        # employees = Employee.objects.extra(where=['first_name ILIKE %s'], params=[search_term])

        html = render_to_string('app/search_employees.html',
        {'employees':employees})

        return HttpResponse(html)

