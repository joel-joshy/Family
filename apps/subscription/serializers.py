from rest_framework import serializers

from apps.subscription.models import Plan


class PlanListSerializer(serializers.ModelSerializer):
    """
    To list plans
    """
    class Meta:
        model = Plan
        fields = ['name', 'price', 'max_members', 'term', 'stripe_id',
                  'is_active']


class CreateSubscriptionSerializer(serializers.Serializer):
    """
    To crete a customer subscription in stripe
    """
    price_id = serializers.CharField()