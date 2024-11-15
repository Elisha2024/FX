from rest_framework import serializers
from .models import FXTransaction

class FXTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FXTransaction
        fields = '__all__'
        read_only_fields = ['identifier', 'date_of_transaction']


class CurrencyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=3)


# serializers.py
from rest_framework import serializers

class CurrencyConversionSerializer(serializers.Serializer):
    customer_id = serializers.CharField(required=True)
    input_amount = serializers.FloatField(required=True)
    input_currency = serializers.CharField(max_length=3, required=True)
    output_currency = serializers.CharField(max_length=3, required=True)



