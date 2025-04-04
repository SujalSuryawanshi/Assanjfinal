from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DeleteView, UpdateView, View, ListView, DetailView
from django.contrib.auth.views import PasswordResetView
from .models import Category, Staller, MenuItems, Following, Order, Rating, FooRating,Foo_Category,New_offer, UserLike, Cart, CartItem  
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.models import CustomUser, FriendRequest, CustomUser, EmailVerification
from users.forms import UserSearchForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.conf import settings
from django.contrib.auth import authenticate
from .forms import StallerForm,SignInForm, RatingForm, AddItemForm, MenuRatingForm, FooCategoryForm,NewOfferForm,EditOfferForm, CustomUserCreationForm, OTPForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Avg
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail  # Import for sending email
from django.utils.crypto import get_random_string 
from django.contrib.auth.models import Group
from datetime import date,timedelta
from django.http import HttpResponse


from django.views.decorators.csrf import csrf_exempt
##PAYMENTS##
import json, requests
from datetime import timedelta
import razorpay
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import timedelta
from .models import Subscription
from django.conf import settings
from django.http import JsonResponse



#VIEWS
class Home(View):
    def get(self, request):
        is_owner = request.user.groups.filter(name='Owner').exists()
        is_member=request.user.groups.filter(name='Member').exists()
        sort_by = request.GET.get('sort_by', '')
        stalls = Staller.objects.all()
        cat = Category.objects.all()
        popu = Staller.objects.filter(Q(category__cat_name__icontains='Popular'))
        item = MenuItems.objects.all()

        if sort_by == 'ratings_high_to_low':
            stalls = stalls.order_by('-rating')
            popu = stalls.order_by('-rating')
        
        elif sort_by == 'ratings_low_to_high':
            stalls = stalls.order_by('rating')
            popu = stalls.order_by('rating')
        elif sort_by == 'followers_high_to_low':
            stalls = sorted(stalls, key=lambda x: x.followers.count(), reverse=True)
            popu = sorted(stalls, key=lambda x: x.followers.count(), reverse=True)
        elif sort_by == 'followers_low_to_high':
            stalls = sorted(stalls, key=lambda x: x.followers.count())
            popu = sorted(stalls, key=lambda x: x.followers.count())

        # Adding follow_count for each staller
        stalls_with_follow_count = []
        for stall in stalls:
            stall_dict = {
                'stall': stall,
                'follow_count': stall.followers.count()
            }
            stalls_with_follow_count.append(stall_dict)

        popu_stalls_with_follow_count = []
        for popu_stall in popu:
            popu_stall_dict = {
                'popu_stall': popu_stall,
                'follow_count': popu_stall.followers.count()
            }
            popu_stalls_with_follow_count.append(popu_stall_dict)

        context = {
            'stalls_with_follow_count': stalls_with_follow_count,
            'popu_stalls_with_follow_count': popu_stalls_with_follow_count,
            'cat': cat,
            'item': item,
            'popu': popu,
            'sort_by': sort_by,
            'is_owner': is_owner,
            'is_member': is_member,
        }

        return render(request, 'main/index.html', context)


###    EDIT_VIEW     ###
##Staller##

class EditStall(UpdateView):
    model = Staller
    form_class = StallerForm
    template_name = 'edits/editinfo.html'

    def form_valid(self, form):
        form.instance.latitude = self.request.POST.get('latitude', form.instance.latitude)
        form.instance.longitude = self.request.POST.get('longitude', form.instance.longitude)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('detail', kwargs={'name': self.object.name})

##Menu-Item##
@login_required
def edit_menu_item(request, name):
    staller = Staller.objects.filter(owner=request.user).first()
    menu_item = get_object_or_404(MenuItems, name=name, owner__owner=request.user)  # Ensure the user owns the item

    if request.method == 'POST':
        form = AddItemForm(request.POST, request.FILES, instance=menu_item)  # Load the existing item into the form
        if form.is_valid():
            form.save()  # Save the changes
            return redirect('detail', name=menu_item.owner)  # Redirect to the staller's detail page
    else:
        form = AddItemForm(instance=menu_item)  # Load the existing item into the form
        form.fields['foo_cat'].queryset = Foo_Category.objects.filter(sh_owner=staller)

    return render(request, 'edits/edititem.html', {'form': form, 'menu_item': menu_item})
####____USER
from .forms import CustomUserEditForm

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile', username=request.user.username)  # Redirect to the profile page or wherever you want
    else:
        form = CustomUserEditForm(instance=request.user)

    return render(request, 'edits/edit_user.html', {'form': form}) 


### Add-In-Views ####

###MENU-ITEM###
@login_required 
def add_menu_item(request, staller_id):
    staller = get_object_or_404(Staller, id=staller_id, owner=request.user)
    
    if request.method == 'POST':
        form = AddItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.owner = staller  # Set the owner to the retrieved staller
            menu_item.save()  # Save the menu item to the database
            return redirect('detail', name=staller.name)
    else:
        # Initialize the form and filter the foo_cat field based on the staller
        form = AddItemForm()
        form.fields['foo_cat'].queryset = Foo_Category.objects.filter(sh_owner=staller)

    return render(request, 'add/additem.html', {'form': form, 'staller': staller})


###foo_Category##

@login_required
def add_foo_category(request):
    if request.method == 'POST':
        form = FooCategoryForm(request.POST)
        if form.is_valid():
            foo_category = form.save(commit=False)
            staller = Staller.objects.filter(owner=request.user).first()  # Use first() to get the first instance
            if staller:
                foo_category.sh_owner = staller
                foo_category.save()
                return redirect(reverse('detail', kwargs={'name': staller.name}))  # Redirect to ListView
            else:
                form.add_error(None, 'You must have a Staller profile to add a Foo Category.')
    else:
        form = FooCategoryForm()
    
    return render(request, 'add/add_foo_category.html', {'form': form})


@login_required
def delete_menu_item(request, item_id):
    menu_item = get_object_or_404(MenuItems, id=item_id, owner__owner=request.user)  # Ensure the user owns the item
    if request.method == 'POST':
        menu_item.delete()  # Delete the item
        return redirect('detail', name=menu_item.owner)  # Redirect to the staller's detail page
    return render(request, 'delete/confirm_delete.html', {'menu_item': menu_item})

### Detail_View ###
class ListView(DetailView):
    model = Staller
    template_name = 'main/detailview.html'
    context_object_name = 'stall'
    slug_field = 'name'
    slug_url_kwarg = 'name'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staller = self.get_object()
        cart = Cart.objects.filter(user=self.request.user, related=staller.id).first()
        
        # Ensure cart_items contains only menu item IDs
        
        items = CartItem.objects.filter(cart__user=self.request.user)  # Ensure it's a QuerySet
        item_ids_in_cart = list(items.values_list('menu_item__id', flat=True))  
    


        
        if self.request.user.is_authenticated:
            is_following = Following.objects.filter(user=self.request.user, staller=staller).exists()
            try:
                rating = Rating.objects.get(user=self.request.user, staller=staller)
                form = RatingForm(instance=rating)
            except Rating.DoesNotExist:
                form = RatingForm()

            menu_rating_forms = {}
            for item in staller.menu_items.all():
                try:
                    menu_rating = FooRating.objects.get(user=self.request.user, menu=item)
                    menu_rating_forms[item.id] = MenuRatingForm(instance=menu_rating, prefix=f'menu_{item.id}')
                except FooRating.DoesNotExist:
                    menu_rating_forms[item.id] = MenuRatingForm(prefix=f'menu_{item.id}')
        else:
            is_following = False
            form = None
            menu_rating_forms = {}
        
        users = CustomUser.objects.all()
        category=Category.objects.all()
        context['category']=category
        context['cart']=cart
        context['items']=items
        context['cart_items'] = item_ids_in_cart  # Pass as a list of IDs
        context['item_ids_in_cart'] = item_ids_in_cart
        context['offers']=staller.offers.all()
        context['menu_items'] = staller.menu_items.all()
        context['is_following'] = is_following
        context['follow_count'] = staller.followers.count()
        context['users'] = users
        context['form'] = form
        context['menu_rating_forms'] = menu_rating_forms
        context['staller_rating_count'] = staller.ratings.count()
        menu_rating_counts = {item.id: item.foo_ratings.count() for item in staller.menu_items.all()}
        context['menu_rating_counts'] = menu_rating_counts
        context['menu_items_by_category'] = {}
        for item in staller.menu_items.all():
            category = item.foo_cat
            if category not in context['menu_items_by_category']:
                context['menu_items_by_category'][category] = []
            context['menu_items_by_category'][category].append(item)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        staller = self.object
        form = RatingForm(request.POST)
        
        if form.is_valid():
            rating, created = Rating.objects.get_or_create(user=request.user, staller=staller)
            rating.rating = form.cleaned_data['rating']
            rating.save()
            staller.update_rating()  # Update the staller's rating
            messages.success(request, 'Rating for staller submitted successfully.')
            return redirect('detail', name=staller.name)
        
        for item in staller.menu_items.all():
            menu_form = MenuRatingForm(request.POST, prefix=f'menu_{item.id}')
            if menu_form.is_valid():
                foo_rating, created = FooRating.objects.get_or_create(user=request.user, menu=item)
                foo_rating.rating = menu_form.cleaned_data['rating']  # Corrected the field name
                foo_rating.save()
                item.update_rating()  # Corrected the method name
                messages.success(request, f'Rating for {item.name} submitted successfully.')
        
        return self.get(request, *args, **kwargs)



#####    LOG_IN,LOG_OUT, REGISTER   #####

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User will be activated after OTP verification
            user.save()

            # Generate and save OTP
            otp = get_random_string(length=6, allowed_chars='1234567890')
            EmailVerification.objects.create(user=user, otp=otp)

            # Send OTP via email
            send_mail(
                'Your OTP for Email Verification',
                f'Your OTP is {otp}',
                'from@example.com',  # Set your "from" email here
                [user.email],
                fail_silently=False,
            )

            messages.success(request, 'Account created! Please verify your email by entering the OTP sent.')
            return redirect('register/verify_otp', user_id=user.id)
    else:
        form = CustomUserCreationForm()

    return render(request, 'register/register.html', {'form': form})




def verify_otp(request, user_id):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        otp_entered = request.POST.get('otp')
        try:
            user = CustomUser.objects.get(id=user_id)
            verification = EmailVerification.objects.get(user=user)

            # Correctly access the is_expired property (without parentheses)
            if verification.is_expired:
                messages.error(request, 'OTP has expired.')
                return redirect('resend_otp')

            # Check if the OTP entered matches
            if verification.otp == otp_entered:
                user.is_active = True  # Activate the user after successful OTP
                user.save()
                messages.success(request, 'Your email has been verified successfully!')
                return redirect('login')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')

        except CustomUser.DoesNotExist:
            messages.error(request, 'User does not exist.')
        except EmailVerification.DoesNotExist:
            messages.error(request, 'No OTP record found for this user.')
    else:
        form = OTPForm()

    return render(request, 'verify_otp.html',{'form': form})


##ADD
def resend_otp_view(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        otp = get_random_string(length=6, allowed_chars='0123456789')
        EmailVerification.objects.update_or_create(user=user, defaults={'otp': otp})

        # Send the new OTP via email
        send_mail(
            'Your OTP Code',
            f'Your new OTP is: {otp}',
            'from@example.com',  # Replace with your sender email
            [user.email],
            fail_silently=False,
        )
        messages.success(request, 'OTP has been resent to your email.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'User does not exist.')

    return redirect('verify_otp', user_id=user_id)  


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            user.current_session_key = request.session.session_key
            user.save(update_fields=['current_session_key'])
            auth_hash = user.get_session_auth_hash()

            # Get the next parameter or redirect to 'home'
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, 'register/login.html', {'form': form})


def logout_view(request):
    user = request.user
    if user.is_authenticated:
        user.current_session_key = None
        user.save(update_fields=['current_session_key'])
    auth_logout(request)
    messages.success(request, 'Your are logged out!')
    return redirect('home')




###  FRIEND_REQUEST, Profiles, Owner_profile    ###


def my_orders(request, username):
    user = CustomUser.objects.get(username=username)
    cart = Cart.objects.filter(user=user)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    current = timezone.now()

    # Check if each order is older than 60 minutes
    for order in orders:
        order.is_old = (current - order.created_at) > timedelta(minutes=600)

    context = {
        'orders': orders,
        'cart': cart,
        'current': current,
    }
    return render(request, 'profile/my_orders.html', context)


@login_required
def order_details(request, order_number):
    # Get the order
    order = get_object_or_404(Order, order_number=order_number)

    # Get the associated cart
    cart = Cart.objects.filter(order=order).first()

    # Get the cart items
    cart_items = cart.cart_items.all() if cart else []

    context = {
        'order': order,
        'cart_items': cart_items,
    }
    return render(request, 'profile/order_details.html', context)

def profile_view(request, username):
    user = get_object_or_404(CustomUser, username=username)
    form = UserSearchForm()
    friend_requests_sent = FriendRequest.objects.filter(from_user=request.user)
    friend_requests_received = FriendRequest.objects.filter(to_user=request.user)
    followed_stallers = Staller.objects.filter(followers__user=user)
    friends = user.friends.all()
    orders=Order.objects.filter(user=user)

    context={
        'profile_user': user,
        'orders': orders,
        'form': form,
        'friend_requests_sent': friend_requests_sent,
        'friend_requests_received': friend_requests_received,
        'friends': friends,
        'followed_stallers': followed_stallers,
    }
    return render(request, 'profile/profile.html', context)

def user_profile(request, username):
    user = get_object_or_404(CustomUser, username=username)
    followed_stallers = Staller.objects.filter(followers__user=user)
    context={
            'usered': user, 
            'followed_stallers': followed_stallers
            }
    return render(request, 'profile/user_profile.html', context)



@login_required
def send_friend_request(request):
    if request.method == 'POST':
        to_username = request.POST.get('to_user')
        to_user = get_object_or_404(CustomUser, username=to_username)
        FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    return redirect('profile', username=request.user.username)


@login_required
def accept_friend_request(request):
    if request.method == 'POST':
        data = json.loads(request.body)  
        friend_request_id = data.get('request_id')
        friend_request = get_object_or_404(FriendRequest, id=friend_request_id)

        if friend_request.to_user == request.user:
            request.user.friends.add(friend_request.from_user)
            friend_request.from_user.friends.add(request.user)
            friend_request.delete()
            return JsonResponse({"message": "Friend request accepted."}, status=200)

    return JsonResponse({"error": "Invalid request."}, status=400)

@login_required
def delete_friend_request(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request_id = data.get('request_id')

        if not request_id:
            return JsonResponse({"error": "Missing request_id."}, status=400)

        friend_request = get_object_or_404(FriendRequest, id=request_id)

        if friend_request.from_user == request.user or friend_request.to_user == request.user:
            friend_request.delete()
            return JsonResponse({"message": "Friend request declined."}, status=200)

        return JsonResponse({"error": "Not authorized."}, status=403)

    return JsonResponse({"error": "Invalid method. POST required."}, status=405)

@login_required
def per_del_friend(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        friend_id = data.get('friend_id')

        if not friend_id:
            return JsonResponse({"error": "Missing friend_id."}, status=400)

        friend = get_object_or_404(CustomUser, id=friend_id)

        if request.user.friends.filter(id=friend.id).exists():
            request.user.friends.remove(friend)
            friend.friends.remove(request.user)
            return JsonResponse({"message": "Friend removed successfully."}, status=200)

    return JsonResponse({"error": "Invalid request."}, status=400)


###SEARCH_
@login_required
def search_users(request):
    form = UserSearchForm(request.GET)
    results = []
    if form.is_valid():
        results = form.search()
        user_friends = request.user.friends.all()
        results = results.exclude(id__in=user_friends.values_list('id', flat=True)).exclude(id=request.user.id)

    return render(request, 'search_results.html', {'form': form, 'results': results})


def search(request):
    categor = Category.objects.all()
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')

    if query:
        stallers = Staller.objects.filter(
            Q(name__icontains=query) | 
            Q(address__icontains=query) | 
            Q(keywords__icontains=query)|
            Q(category__cat_name__icontains=query)|
            Q(loc_cat__name__icontains=query)
        )

        if sort_by == 'ratings_high_to_low':
            stallers = stallers.order_by('-rating')
        elif sort_by == 'ratings_low_to_high':
            stallers = stallers.order_by('rating')
        elif sort_by == 'followers_high_to_low':
            stallers = sorted(stallers, key=lambda x: x.followers.count(), reverse=True)
        elif sort_by == 'followers_low_to_high':
            stallers = sorted(stallers, key=lambda x: x.followers.count())

        menuitems = MenuItems.objects.filter(
            Q(name__icontains=query) |
            Q(foo_cat__foo_name__icontains=query)|
            Q(description__icontains=query)
        )
        menu_rating_counts = {item.id: item.foo_ratings.count() for item in menuitems}
        stalls_with_follow_count = []
        for stall in stallers:
            stall_dict = {
                'stall': stall,
                'follow_count': stall.followers.count()
            }
            stalls_with_follow_count.append(stall_dict)
    else:
        stallers = Staller.objects.none()
        menuitems = MenuItems.objects.none()
        menu_rating_counts = {}

    context = {
        'stallers': stallers,
        'menuitems': menuitems,
        'menu_rating_counts': menu_rating_counts,
        'query': query,
        'stalls_with_follow_count': stalls_with_follow_count,
        'categor': categor,
        'sort_by': sort_by,
    }

    return render(request, 'search.html', context)




###((((STALL FOLLOWING))))####


class FollowStallerView(LoginRequiredMixin, View):
    def post(self, request, name):
        staller = get_object_or_404(Staller, name=name)
        Following.objects.get_or_create(user=request.user, staller=staller)
        return redirect('detail', name=staller.name)

class UnfollowStallerView(LoginRequiredMixin, View):
    def post(self, request, name):
        staller = get_object_or_404(Staller, name=name)
        Following.objects.filter(user=request.user, staller=staller).delete()
        return redirect('detail', name=staller.name)
    




def future(request):
    return render(request,'main/future.html')




# Offers
class OfferView(View):
    def get(self, request, name):
        staller = get_object_or_404(Staller, name=name)
        offers = staller.offers.order_by('-last_updated')
        context = {
            'staller': staller,
            'offers': offers,
        }
        return render(request, 'offer/offers.html', context)
    

class NewOfferView(View):
    def get(self, request, staller_name):
        staller = get_object_or_404(Staller, name=staller_name)
        if staller.owner != request.user:
            return redirect('home')
        form = NewOfferForm()
        return render(request, 'add/new_offer.html', {'form': form, 'staller': staller})

    def post(self, request, staller_name):
        staller = get_object_or_404(Staller, name=staller_name)
        if staller.owner != request.user:
            return redirect('home')
        form = NewOfferForm(request.POST, request.FILES)
        if form.is_valid():
            new_offer = form.save(commit=False)
            new_offer.owner = staller
            new_offer.save()
            return redirect('offers', name=staller.name)
        return render(request, 'add/new_offer.html', {'form': form, 'staller': staller})
    
class EditOfferView(View):
    def get(self, request, offer_id):
        offer = get_object_or_404(New_offer, id=offer_id)
        if offer.owner.owner != request.user:
            return redirect('home')
        form = EditOfferForm(instance=offer)
        return render(request, 'edits/edit_offer.html', {'form': form, 'offer': offer})

    def post(self, request, offer_id):
        offer = get_object_or_404(New_offer, id=offer_id)
        if offer.owner.owner != request.user:
            return redirect('home')
        form = EditOfferForm(request.POST, request.FILES, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('offers', name=offer.owner.name)
        return render(request, 'edits/edit_offer.html', {'form': form, 'offer': offer})

@login_required
def delete_offer(request, offer_id):
    offer = get_object_or_404(New_offer, id=offer_id)
    if offer.owner.owner != request.user:
        return redirect('home')

    if request.method == 'POST':
        offer.delete()
        return redirect('offers', name=offer.owner.name)
    
    return render(request, 'delete/delete_offer.html', {'offer': offer})






def cat_view(request, foo):
    categor = Category.objects.get(cat_name=foo)
    stalls = Staller.objects.filter(category=categor)
    sort_by = request.GET.get('sort_by', '')
    category = Category.objects.all()


    if sort_by == 'ratings_high_to_low':
        stalls = stalls.order_by('-rating')
    elif sort_by == 'ratings_low_to_high':
        stalls = stalls.order_by('rating')
    elif sort_by == 'followers_high_to_low':
        stalls = sorted(stalls, key=lambda x: x.followers.count(), reverse=True)
    elif sort_by == 'followers_low_to_high':
        stalls = sorted(stalls, key=lambda x: x.followers.count())


    stalls_with_follow_count = []
    for stall in stalls:
        stall_dict = {
            'stall': stall,
            'follow_count': stall.followers.count()
        }
        stalls_with_follow_count.append(stall_dict)

    context = {
        'stalls_with_follow_count': stalls_with_follow_count,
        'stalls': stalls,
        'categor': categor,
        'category': category,
        'sort_by': sort_by,
    }

    return render(request, 'category.html', context)



def custom_404(request, exception):
    return render(request, '404.html', status=404)


# Reset_Password

class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'register/custom_password_reset_email.html'
    subject_template_name = 'register/custom_password_reset_subject.txt'  # optional, see below for subject change logic

    def get_email_options(self):
        options = super().get_email_options()
        
        # Set your custom domain here (if necessary)
        options['domain'] = 'https://www.assanj.in/'

        # Change the subject here
        options['subject'] = 'Custom Password Reset Request - Assanj'

        return options




def pay_page_view(request, staller_id):
    obj = Staller.objects.get(pk=staller_id)
    return render(request, 'payments/paypage.html', {'object': obj})

def google_login(request):
    return render(request,"google_login.html")



##PAYMENTS##



# Razorpay client setup
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Define prices for different plans
plan_prices = {
    'monthly': 30,
    'quarterly': 100,
    'yearly': 300
}

def subscription_page(request):
    return render(request, 'payments/subscription_page.html', {'plans': plan_prices})


def verify_payment(request):
    transaction_id = request.GET.get('transaction_id')
    
    if not transaction_id:
        return JsonResponse({"success": False, "error": "Missing transaction ID"})
    
    # Simulate checking payment status (Replace with real API check)
    payment_verified = True  # Assume success for now

    if payment_verified:
        cart_id = request.session.get("cart_id")  # Ensure cart ID is stored in session
        if not cart_id:
            return JsonResponse({"success": False, "error": "Cart ID missing"})

        try:
            cart = Cart.objects.get(id=cart_id)
            total_amount = cart.total_price()

            # Create Order
            order = Order.objects.create(
                user=cart.user,
                stall=cart.related,
                total_price=total_amount,
                transaction_id=transaction_id
            )

            cart.order = order  # Link cart to order
            cart.save()

            # Destroy the QR code (Assuming it's stored in session)
            request.session.pop("qr_code", None)

            # Notify stall owner
            notify_stall_owner(order)

            return JsonResponse({"success": True, "message": "Order created successfully!"})

        except Cart.DoesNotExist:
            return JsonResponse({"success": False, "error": "Cart not found"})
    
    return JsonResponse({"success": False, "error": "Payment verification failed"})


#stupid

def terms_and_conditions(request):
    return render(request, 'stupid/terms_and_conditions.html')

def privacy_policy(request):
    return render(request, 'stupid/privacy_policy.html')

def refund_cancellation_policy(request):
    return render(request, 'stupid/refund_cancellation_policy.html')

def contact_page(request):
    return render(request, 'stupid/contact_us.html')


# CART



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # Only if necessary, better to use CSRF token in AJAX
def add_to_cart(request, item_id):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "User not authenticated"}, status=403)

    try:
        menu_item = MenuItems.objects.get(id=item_id)
        cart, created = Cart.objects.get_or_create(user=request.user, related=menu_item.owner)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)

        if created:
            in_cart = True  # Item was added
        else:
            cart_item.delete()
            in_cart = False  # Item was removed

        return JsonResponse({"success": True, "in_cart": in_cart})
    except MenuItems.DoesNotExist:
        return JsonResponse({"success": False, "error": "Item not found"}, status=404)




@login_required
def view_cart(request, staller_id):
    cart = Cart.objects.filter(user=request.user, related=staller_id).first()
    items = cart.cart_items.all() if cart else []
    total_price = sum(item.quantity * item.menu_item.normal_price for item in items) 
    if (total_price >= 0):
        total_price_true=True   
    context={
        'cart':cart,
        'items':items,
        'total_price':total_price,
        'total_price_true':total_price_true,
    }
    
    return render(request, 'cart/view_cart.html', context)

@csrf_exempt
@login_required
def update_quantity(request, cart_item_id, change):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
        if int(change) == 1:
            cart_item.quantity += 1
        elif int(change) == -1 and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()

        total_price = cart_item.quantity * cart_item.menu_item.normal_price
        cart_total = sum(item.quantity * item.menu_item.normal_price for item in cart_item.cart.cart_items.all())

        return JsonResponse({
            'success': True,
            'quantity': cart_item.quantity,
            'total_price': total_price,
            'cart_total': cart_total
        })
    return JsonResponse({'success': False}, status=400)

@csrf_exempt
@login_required
def remove_from_cart(request, cart_item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
        cart = cart_item.cart
        cart_item.delete()

        cart_total = sum(item.quantity * item.menu_item.normal_price for item in cart.cart_items.all())

        return JsonResponse({'success': True, 'cart_total': cart_total})
    return JsonResponse({'success': False}, status=400)


# ORDERS


@login_required
def stall_owner_orders(request, staller_id):
    stall_owner = get_object_or_404(Staller, id=staller_id)
    
    # Get all orders for this stall owner
    orders = Order.objects.filter(stall_owner=stall_owner).order_by('-created_at')
    
    return render(request, 'stall_owner_orders.html', {'orders': orders})



@login_required
def update_order_status(request, order_id, status):
    """ Updates order status and clears cart if order is completed. """
    order = get_object_or_404(Order, id=order_id)

    if request.user == order.stall_owner.owner:  # Ensure the stall owner is updating their own orders
        order.status = status
        order.save()

            

        return JsonResponse({'success': True, 'status': order.status, 'order_number': order.order_number})
    
    return JsonResponse({'success': False, 'message': 'You do not have permission to update this order.'}, status=403)



import random
from decimal import Decimal, InvalidOperation
from urllib.parse import quote
import uuid


@login_required
@csrf_exempt  # Optional: If CSRF is causing issues, enable this
def process_payment(request, staller_id):
    """Handles UPI payment processing and generates a payment link."""

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'}, status=400)

    # Fetch the stall owner
    stall_owner = get_object_or_404(Staller, id=staller_id)

    # Extract JSON data
    try:
        data = json.loads(request.body)
        amount = float(data.get('amount', 0))  # Get amount from frontend
        if amount <= 0:
            return JsonResponse({'success': False, 'message': 'Invalid payment amount'}, status=400)
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)

    # Fetch UPI ID of stall owner
    upi_id = stall_owner.upi_id  
    if not upi_id:
        return JsonResponse({'success': False, 'message': 'UPI ID not found for stall owner'}, status=400)

    # ✅ Generate a unique UPI Payment Link
    transaction_id = str(random.randint(10000, 99999))
    transaction_id = str(uuid.uuid4())
    upi_link = f"upi://pay?pa={upi_id}&tid={transaction_id}&am={amount}&cu=INR"

    # ✅ Ensure Cart Exists Before Creating Order
    cart = Cart.objects.filter(user=request.user, related=stall_owner).first()
    if not cart:
        return JsonResponse({'success': False, 'message': 'No cart found for this user'}, status=400)

    # ✅ Create Order Linked to Cart
    try:
        total_amount = Decimal(str(amount))
        order = Order.objects.create(
            order_number=str(random.randint(10000, 99999)),  # Use transaction_id as order_number
            user=request.user,
            stall_owner=stall_owner,
            total_amount=total_amount,
            status='in_process'  # Mark as pending until verified
        )
        cart.order = order  # Link the cart to the order
        cart.save()
    except InvalidOperation:
        return JsonResponse({'success': False, 'message': 'Invalid amount format'}, status=400)

    # ✅ Return UPI Link to Frontend
    return JsonResponse({'success': True, 'upi_link': upi_link})




# Replace with actual UPI API details
UPI_COLLECT_API_URL = "https://api.example.com/upi/collect"
API_KEY = "your_api_key_here"

def create_upi_collect_request(request):
    data = json.loads(request.body)
    order_number = str(random.randint(10000, 99999))
    amount = data["amount"]
    customer_upi = data["customer_upi"]
    stall_owner_id = data["stall_owner_id"]

    # Get Stall Owner details
    try:
        stall_owner = Staller.objects.get(id=stall_owner_id)
    except Staller.DoesNotExist:
        return JsonResponse({"error": "Stall owner not found"}, status=400)

    # Create Order in DB (mark as PENDING)
    order = Order.objects.create(
        order_number=order_number, stall_owner=stall_owner, total_amount=amount, status_pay="PENDING"
    )

    payload = {
        "merchant_id": "your_merchant_id",
        "order_id": order_number,
        "amount": amount,
        "customer_upi": customer_upi,
        "merchant_upi": stall_owner.upi_id,  # Direct settlement to owner's UPI ID
        "callback_url": "http://127.0.0.1:8000//payment/callback/"
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(UPI_COLLECT_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        return JsonResponse({"message": "Payment request sent", "order_number": order_number})
    else:
        order.status_pay = "FAILED"
        order.save()
        return JsonResponse({"error": "Payment request failed"}, status=400)
    
def payment_callback(request):
    data = json.loads(request.body)
    order_number = data["order_id"]

    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found"}, status=404)

    if data["status"] == "SUCCESS":
        order.status_pay = "SUCCESS"
        order.status = "done"
        order.save()
        return JsonResponse({"message": "Payment Successful"}, status=200)

    order.status_pay = "FAILED"
    order.save()
    return JsonResponse({"message": "Payment Failed"}, status=400)



def payment_status(request):
    # Simulate checking payment status from UPI (this needs integration)
    payment_success = True  # Change this based on actual UPI verification

    if payment_success:
        return JsonResponse({"status": "SUCCESS"})
    else:
        return JsonResponse({"status": "FAILED"})


@csrf_exempt
def create_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        cart_id = data.get("cart_id")
        
        # Create order in database
        cart = Cart.objects.get(id=cart_id)
        new_order = Order.objects.create(user=cart.user, total_amount=cart.total_amount(), stall_owner=cart.related.owner)
        
        # Clear the cart after order creation
        cart.items.clear()
        
        return JsonResponse({"status": "ORDER_CREATED", "order_id": new_order.id})

def notify_stall_owner(order):
    stall_owner = order.stall.owner
    message = f"New Order Received! Order ID: {order.id}, Total: ₹{order.total_price}"
    
    # Send a notification (Assume SMS/WhatsApp API)
    print(f"📢 Sending notification to {stall_owner.phone}: {message}")


@csrf_exempt  # Only for testing, use proper CSRF handling in production
# def update_location(request, stall_id):
#     if request.method == "POST":
#         print(f"Received request for stall_id: {stall_id}")  # Debug log

#         try:
#             stall = Staller.objects.get(id=stall_id)
#             latitude = request.POST.get("latitude")
#             longitude = request.POST.get("longitude")

#             print(f"Received lat: {latitude}, lon: {longitude}")  # Debug log

#             if not latitude or not longitude:
#                 return JsonResponse({"status": "error", "message": "Latitude or longitude missing"}, status=400)

#             stall.latitude = latitude
#             stall.longitude = longitude
#             stall.save()

#             print("Location updated successfully!")  # Debug log
#             return JsonResponse({"status": "success", "latitude": stall.latitude, "longitude": stall.longitude})

#         except Staller.DoesNotExist:
#             return JsonResponse({"status": "error", "message": "Stall not found"}, status=404)

#     return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


def update_location(request, stall_id):
    if request.method == 'POST':
        try:
            stall = get_object_or_404(Staller, pk=stall_id)
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            stall.latitude = latitude
            stall.longitude = longitude
            stall.save()
            return JsonResponse({'success': True})
        except Staller.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Stall not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    

def posts(request):
    offers=New_offer.objects.filter(owner__owner = 1)
    return render(request,'offer/offers.html',{'offers':offers})





from collections import defaultdict

def dash_prof(request, username):
    user = get_object_or_404(CustomUser, username=username)

    # Friend request statistics
    friend_requests_sent = FriendRequest.objects.filter(from_user=user).count()
    friend_requests_received = FriendRequest.objects.filter(to_user=user).count()
    pending_requests = FriendRequest.objects.filter(to_user=user, status="Pending").count()
    total_friends = user.friends.all().count()
    rank = user.friends.all().order_by('-points')

    # Preparing Data for Charts
    plot_friend = user.friends.all()
    friend_names = [friend.username for friend in plot_friend]  
    friend_points = [friend.points for friend in plot_friend]  

    # Points history (simulated constant values for now)
    points_history = [100] * 30  
    dates_labels = [f"Day {i+1}" for i in range(30)]  # Dummy x-axis labels

    # Convert lists to JSON format
    context = {
        "profile_user": user,
        "total_friends": total_friends,
        "friend_requests_sent": friend_requests_sent,
        "friend_requests_received": friend_requests_received,
        "pending_requests": pending_requests,
        "points_history": json.dumps(points_history),  
        "dates_labels": json.dumps(dates_labels),
        'rank': rank,
        'friend_names': json.dumps(friend_names),  
        'friend_points': json.dumps(friend_points),  
    }
    return render(request, "profile/dashboard.html", context)