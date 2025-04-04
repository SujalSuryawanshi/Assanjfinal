from django.contrib import admin
from django.urls import path, include
from .views import Home,login_view, logout_view,send_friend_request, accept_friend_request, delete_friend_request,ListView,FollowStallerView,UnfollowStallerView,register,cat_view, resend_otp_view
from .views import EditStall,add_menu_item, delete_menu_item,edit_menu_item,future,add_foo_category,OfferView, NewOfferView, EditOfferView, delete_offer, edit_profile,  pay_page_view, update_location
from . import views
from allauth.socialaccount.providers.google.views import oauth2_login
urlpatterns = [
    path("",Home.as_view(), name='home' ),
    path('register/', views.register, name='register'),
    path('verify-otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path('resend-otp/<int:user_id>/', resend_otp_view, name='resend_otp'),
    path('accounts/login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path("place/<slug:name>/", ListView.as_view(), name="detail"),
    path('search', views.search , name='search'),
    path('search/', views.search_users, name='search_users'),
    

    #Friends
    path('send_request/', views.send_friend_request, name='send_friend_request'),
     path('accept_request/', views.accept_friend_request, name='accept_friend_request'),
    path('delete_request/', views.delete_friend_request, name='delete_friend_request'),
    path('per_del/', views.per_del_friend, name='per_del_friend'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/look/<str:username>/', views.user_profile, name='user_profile'),
    
    path('edit/<int:pk>',EditStall.as_view() , name='edit_info'),
    path("update-location/", update_location, name="update_location"),
    
    path('stallers/<str:name>/follow/', FollowStallerView.as_view(), name='follow_staller'),
    path('stallers/<str:name>/unfollow/', UnfollowStallerView.as_view(), name='unfollow_staller'),
    
    path('staller/<int:staller_id>/add_menu_item/', add_menu_item, name='add_menu_item'),
    path('delete-menu-item/<int:item_id>/', delete_menu_item, name='delete_menu_item'),
    
    path('edit-menu-item/<str:name>/', edit_menu_item, name='edit_menu_item'),
    path('add-foo-category/', add_foo_category, name='add_foo_category'),
    path('stall/<slug:name>/offers/', OfferView.as_view(), name='offers'),
    path('stall/<slug:staller_name>/new_offer/', NewOfferView.as_view(), name='new_offer'),
    path('offer/<int:offer_id>/edit/', EditOfferView.as_view(), name='edit_offer'),
    path('offer/<int:offer_id>/delete/', delete_offer, name='delete_offer'),
    
    path("future/", views.future, name="future"),
    path("category/<str:foo>/", views.cat_view, name="category"),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path("pay/<int:staller_id>/paypage", pay_page_view, name="pay"),
    # path("accounts/google/login/",views.google_login, name="google_login")
    path('accounts/google/direct-login/', oauth2_login, name='google_direct_login'),

    ##PAYMENTS##
     path('subscription/', views.subscription_page, name='subscription_page'),
    path('create_order/<str:plan_type>/', views.create_order, name='create_order'),
        # path('payment_success/', views.payment_success, name='payment_success'),
        # path('payment_failure/', views.payment_failure, name='payment_failure'),


    #stupid
     path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('refund-cancellation-policy/', views.refund_cancellation_policy, name='refund_cancellation_policy'),
    path('contact-us/', views.contact_page, name='contact_us'),


    #cart
    # path('proceed-to-payment/<int:staller_id>/', views.proceed_to_payment, name='proceed_to_payment'),
    # path('clear-cart/<int:staller_id>/', views.clear_cart, name='clear_cart'),

     path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/<int:staller_id>/items', views.view_cart, name='view_cart'),
    path('cart/update-quantity/<int:cart_item_id>/<str:change>/', views.update_quantity, name='update_quantity'),  # Increase/Decrease quantity
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),  # Remove item from cart 


     path('cart/process-payment/<int:staller_id>/', views.process_payment, name='process_payment'),
    path('stall-owner/orders/<int:staller_id>/', views.stall_owner_orders, name='stall_owner_orders'),

    #PAYMENTS
    path("payment/initiate/", views.create_upi_collect_request, name="initiate_payment"),
    path("payment/callback/", views.payment_callback, name="payment_callback"),

    #MY_ORDERS
    path('order/update-status/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),
    path("order/<int:order_number>", views.order_details , name="order_details"),
    path('my-orders/<str:username>/', views.my_orders, name='my_orders'),

    #Locations
    path('update-location/<int:stall_id>/', update_location, name='update_location'),

    #Posts
    path('post/', views.posts, name='post'),
    path("dash/<str:username>", views.dash_prof, name="dash_profile")
    ]
