from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, UserForm, UserProfileForm
from django.shortcuts import redirect
from django.urls import reverse
from rango.forms import PageForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    context_dict['extra'] = 'From the model solution on GitHub'

    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    # Spoiler: you don't need to pass a context dictionary here.
    return render(request, 'rango/about.html')

def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)

        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['pages'] = None
        context_dict['category'] = None
    
    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
    
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except:
        category = None
    
    # You cannot add a page to a Category that does not exist... DM
    if category is None:
        return redirect(reverse('rango:index'))

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)  # This could be better done; for the purposes of TwD, this is fine. DM.
    
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)
    
    
    
def register(request):
    #a boolean for whether the registration was complete
    registered = False
    
    # It it's a HTTP POST since we're processing form data
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            #save user's form data to database
            user = user_form.save()
            
            #hash password with set_password method and then save
            user.set_password(user.password)
            user.save()
            
            #now sort out the UserProfile isntance
            #we need to set the user attributes ourselves
            #set commit=False to delay saving the model
            #until we're ready to avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user
            
            #did user provide profile pic?
            #if so, get it from input form and put it in UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                
            #now we can save UserPRofile model
            profile.save()
            
            #update our variable to indicate the registration was successful
            registered = True
        
        else:
            #invalid form or forms
            #print problems 
            print(user_form.errors, profile_form.errors)
            
    else:
        #Not HTTP POST, so we render form using 2 ModelForm instances
        #these forms will be blanks, ready for user input
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    #render the template depending on the context
    return render(request,
                    'rango/register.html',
                    context = {'user_form': user_form,
                                'profile_form': profile_form,
                                'registered': registered})
                                
def user_login(request):
    #if the request is a HTTP POST, pull the relevent info
    if request.method == 'POST':
        #get username/password from login form
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            #is the user is active (not disabled #ableism)
            if user.is_active:
                login(request,user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print("Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied")
            
    else:
        return render(request, 'rango/login.html')
     
@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')
    
    
    
@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))