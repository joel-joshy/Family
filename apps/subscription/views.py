import stripe
from django.conf import settings

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.subscription.models import Plan
from apps.subscription.serializers import PlanListSerializer, CreateSubscriptionSerializer
from apps.usermanagement.permissions import IsAnyManager


stripe.api_key = settings.STRIPE_SECRET_KEY


class PlanListView(generics.ListAPIView):
    """
    Plan list api view
    """
    serializer_class = PlanListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Plan.objects.filter(is_active=True)
        term = self.request.query_params.get('term')
        if term == Plan.PER_MONTH:
            queryset = queryset.filter(term=Plan.PER_MONTH)
        elif term == Plan.PER_YEAR:
            queryset = queryset.filter(term=Plan.PER_YEAR)
        return queryset


class CreateSubscriptionView(generics.GenericAPIView):
    """
    To create a customer subscription on stripe with a plan
    """

    permission_classes = [IsAuthenticated, IsAnyManager]
    serializer_class = CreateSubscriptionSerializer

    def post(self, request, *args, **kwargs):
        user = self.request.user
        email = user.email

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        price_id = request.data.get('price_id')
        plan = Plan.objects.get(stripe_id=price_id)
        customer = stripe.Customer.create(
            email=email, name=user.get_full_name()
        )
        stripe_subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[
                {"price": price_id},
            ],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent']
        )
        # import pdb; pdb.set_trace()

        return Response(data={
            'status': True
        })


class StripeSubscriptionCreationWebhookView(APIView):
    """
    Stripe subscription creation and update webhook
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        endpoint_secret = settings.STRIPE_ENDPOINT_KEY
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        import pdb; pdb.set_trace()
        return Response(data={'TRUE'})