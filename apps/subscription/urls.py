from django.urls import path

from apps.subscription import views

urlpatterns = [
    path('plans/', views.PlanListView.as_view(), name='plans'),
    path('create-subscription/', views.CreateSubscriptionView.as_view(),
         name='create_subscription'),
    path('create-or-renew-subscription-webhook/',
         views.StripeSubscriptionCreationWebhookView.as_view(), name='create-or-renew-subscription-webhook')
]