from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import FXTransactionSerializer, CurrencyCodeSerializer, CurrencyConversionSerializer
from .services import get_currency_codes
from rest_framework.generics import GenericAPIView
from .services import get_conversion_rate
from rest_framework import serializers
from .models import FXTransaction
import requests


class TransactionListCreateAPIView(ListCreateAPIView):
    """
    View to list all transactions and create a new transaction.
    """
    queryset = FXTransaction.objects.all()
    serializer_class = FXTransactionSerializer

    def get_queryset(self):
        """
        Optionally filter the queryset by customer_id.
        """
        customer_id = self.request.query_params.get('customer_id', None)
        if customer_id:
            return FXTransaction.objects.filter(customer_id=customer_id)
        return super().get_queryset()

class TransactionDetailAPIView(RetrieveAPIView):
    """
    View to retrieve transactions by customer_id.
    """
    queryset = FXTransaction.objects.all()
    serializer_class = FXTransactionSerializer

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to retrieve transactions by customer_id.
        """
        customer_id = kwargs.get('customer_id')  # Get 'customer_id' from URL
        transactions = FXTransaction.objects.filter(customer_id=customer_id)

        if not transactions.exists():
            return Response({"detail": "Transactions not found for the given customer_id."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CurrencyCodesAPIView(GenericAPIView):
    """
    View to return a list of available currency codes from an external API.
    """
    serializer_class = CurrencyCodeSerializer
    permission_classes = [AllowAny]  # No authentication required

    def get_queryset(self):
        """
        Override to return the currencies fetched from the external API via the service.
        """
        # Fetch currencies from the external API using the service
        currency_data = get_currency_codes()
        
        if "error" in currency_data:
            return []  # Return an empty list if there is an error
        
        return [{"code": currency} for currency in currency_data["currencies"]]

    def get(self, request, *args, **kwargs):
        # Get the currencies via the overridden get_queryset method
        queryset = self.get_queryset()

        if not queryset:
            return Response(
                {"detail": "Failed to retrieve currency codes."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()  # Ensure the data is valid

        return Response(serializer.data, status=status.HTTP_200_OK)




class CurrencyConversionAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CurrencyConversionSerializer

    def post(self, request, *args, **kwargs):
        # Deserialize incoming data
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({"detail": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        # Extract validated data
        customer_id = serializer.validated_data['customer_id']
        input_amount = serializer.validated_data['input_amount']
        input_currency = serializer.validated_data['input_currency']
        output_currency = serializer.validated_data['output_currency']

        # Call the service to get the conversion data
        conversion_data = get_conversion_rate(input_currency, output_currency, input_amount)

        # Handle error from the service
        if "error" in conversion_data:
            return Response(conversion_data, status=status.HTTP_400_BAD_REQUEST)

        # Store conversion in the database
        conversion_record = FXTransaction.objects.create(
            customer_id=customer_id,
            input_amount=input_amount,
            input_currency=input_currency,
            output_amount=conversion_data['converted_amount'],
            output_currency=output_currency
        )

        # Prepare the response data
        response_data = {
            "customer_id": customer_id,
            "input_currency": input_currency,
            "output_currency": output_currency,
            "input_amount": input_amount,
            "output_amount": conversion_data['converted_amount'],
            "rate": conversion_data['rate']
        }

        # Return successful response with conversion details
        return Response(response_data, status=status.HTTP_200_OK)
