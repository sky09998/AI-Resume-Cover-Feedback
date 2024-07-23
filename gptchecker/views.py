from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import chardet
import PyPDF2
import google.generativeai as genai
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserLoginForm, DocumentForm
from .models import Document, UserActivityLog, APIRequestLog, UserM, UserMAdmin, Contact
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from .models import Order

# Configure the Google Generative AI API with the provided key
genai.configure(api_key="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")


def services(request):
    return render(request, 'gptchecker/services.html')

def contact(request):
    return render(request, 'gptchecker/contact.html')

def about(request):
    return render(request, 'gptchecker/about.html')

def dashboard_view(request):
    user_logs = UserActivityLog.objects.all().order_by('-timestamp')[:10]  # Get the latest 10 logs
    api_logs = APIRequestLog.objects.all().order_by('-timestamp')[:10]
    return render(request, 'gptchecker/dashboard.html', {'user_logs': user_logs, 'api_logs': api_logs})

def admin_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:  # Ensure the user is an admin
                login(request, user)
                return HttpResponseRedirect(reverse('admin_login'))  # Redirect to admin dashboard
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'gptchecker/admin_login.html', {'form': form})

def home(request):
    return render(request, 'gptchecker/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            UserActivityLog.objects.create(user=user, activity_type='register', details='User registered successfully.')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            email = request.POST.get('email', '')
            phone = request.POST.get('phone', '')
            contact = UserM(first_name=first_name, last_name=last_name, email=email, phone=phone)
            contact.save()
            return redirect('document_view')
        else:
            print(form.errors)  # Log form errors
    else:
        form = UserRegisterForm()
    return render(request, 'gptchecker/register.html', {'form': form})

def user_dashboard(request):
    usershai = UserM.objects.all()
    document_count = Document.objects.count()
    return render(request, 'gptchecker/user_dashboard.html',{'users': usershai,'dcu':document_count})

# Perform delete operation
def delete_user(request, user_id):
    if request.method == 'POST':
        try:
            user = UserM.objects.get(pk=user_id)
            user.delete()
            messages.success(request, 'User deleted successfully.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    return redirect('user_dashboard')

def registeradmin(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        contact = UserMAdmin(first_name=first_name, last_name=last_name , email=email, phone=phone)
        contact.save()
        if form.is_valid():
            user = form.save()
            login(request, user)
            UserActivityLog.objects.create(user=user, activity_type='register', details='User registered successfully.')
            return redirect(reverse('user_dashboard'))
        else:
            print(form.errors)  # Log form errors
    else:
        form = UserRegisterForm()
    return render(request, 'gptchecker/registeradmin.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                UserActivityLog.objects.create(user=user, activity_type='login', details='User logged in successfully.')
                return redirect('document_view')
    else:
        form = UserLoginForm()
    return render(request, 'gptchecker/login.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        UserActivityLog.objects.create(user=request.user, activity_type='logout', details='User logged out successfully.')
    logout(request)
    return redirect('home')

def contactsend(request):
    name = request.POST.get('name', '')
    email = request.POST.get('email', '')
    desc = request.POST.get('message', '')
    contact = Contact(name=name, email=email, msg=desc)
    contact.save()
    return render(request, 'gptchecker/contactsend.html')

@login_required
def document_view(request):
    feedback = None
    form = DocumentForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        new_doc = form.save(commit=False)
        document_type = form.cleaned_data['document_type']
        file_content = new_doc.uploaded_file.read()

        if new_doc.uploaded_file.name.endswith('.pdf'):
            file_content = extract_text_from_pdf(new_doc.uploaded_file)
        else:
            file_content = safe_text_decode(file_content)

        if document_type == 'resume':
            feedback = get_resume_feedback(request.user, file_content)
        elif document_type == 'cover_letter':
            feedback = get_cover_feedback(request.user, file_content)
        feedback = pretty_print_feedback(feedback)

        new_doc.feedback = feedback
        new_doc.save()
        form = DocumentForm()  # Reset form after submission

    context = {'form': form, 'feedback': feedback}
    return render(request, 'gptchecker/document_view.html', context)

def safe_text_decode(file_content):
    detection = chardet.detect(file_content)
    encoding = detection.get('encoding', 'utf-8')
    return file_content.decode(encoding)

def extract_text_from_pdf(file_stream):
    reader = PyPDF2.PdfReader(file_stream)
    text = [page.extract_text() for page in reader.pages]
    return '\n'.join(text)

def get_resume_feedback(user, text):
    prompt = "Give me feedback for above resume contents"
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat()
    APIRequestLog.objects.create(user=user, request_type="GenAi Req-Resume")
    response = chat.send_message(f"{text}\n{prompt}")
    return response.text

def get_cover_feedback(user, text):
    prompt = "Give me feedback for above cover letter contents"
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat()
    APIRequestLog.objects.create(user=user, request_type="GenAi Req-Cover")
    response = chat.send_message(f"{text}\n{prompt}")
    return response.text

def pretty_print_feedback(feedback_str):
    formatted_feedback = '<div class="feedback">'
    lines = feedback_str.split('\n')
    in_list = False  # Track if we're inside a list

    for line in lines:
        if line.strip():
            # Manage list items
            if line.startswith('* '):
                # Start a new list if not already in one
                if not in_list:
                    in_list = True
                    formatted_feedback += '<ul>'
                line_content = line.replace('* ', '', 1).strip()
                # Handle bold within list items
                line_content = handle_bold(line_content)
                formatted_feedback += f'<li>{line_content}</li>'
            else:
                # Close the list if one was open
                if in_list:
                    formatted_feedback += '</ul>'
                    in_list = False
                # Handle bold without bullet
                line_content = handle_bold(line)
                formatted_feedback += f'<p>{line_content}</p>'
    # Ensure to close any open list tags
    if in_list:
        formatted_feedback += '</ul>'
    formatted_feedback += '</div>'
    return formatted_feedback

def handle_bold(text):
    """Handles toggling of bold formatting within a text based on '**'."""
    if '**' in text:
        # Split the text at each '**' and toggle bolding
        parts = text.split('**')
        bold = False
        result = ""
        for part in parts:
            if bold:
                result += f'<b>{part}</b>'
            else:
                result += part
            bold = not bold  # Toggle bolding
        return result
    else:
        return text

#views-- janv
def calculate_price(pack):
    # Define your pricing logic here based on the selected pack
    if pack == 'starter':
        return 149
    elif pack == 'premium':
        return 219
    elif pack == 'ultimate':
        return 349
    else:
        return 0  # Default price if pack is invalid

# def place_order(request):
#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             order = form.save(commit=False)
#             order.user = request.user
#             order.price = calculate_price(order.pack)  # Implement your own logic to calculate price
#             order.save()
#             # Redirect to a success page or display a success message
#             return redirect('gptchecker/order_success.html')
#     else:
#         form = OrderForm()
#     return render(request, 'your_template.html', {'form': form})

def order_success(request):
    # Render a success page or display a success message
    return render(request, 'gptchecker/order_success.html')

# def payment_form(request):
#     return render(request, 'gptchecker/payment_form.html')


def place_order(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        c_no = request.POST.get('card_number', '')
        ex_mo = request.POST.get('expiry_month', '')
        ex_ye = request.POST.get('expiry_year', '')
        contact = Order(name=name, card_number=c_no, expiry_month=ex_mo, expiry_year=ex_ye)
        contact.save()
        messages.success(request, 'Order placed successfully!')
        return render(request, 'gptchecker/order_success.html')

    return render(request, 'gptchecker/credit_card_form.html')
