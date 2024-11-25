from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.cache import cache
from .serializers import FXTransactionSerializer, CurrencyCodeSerializer, CurrencyConversionSerializer
from .services import get_currency_codes, get_conversion_rate
from .models import FXTransaction, UserCurrencyPreference
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import build_response
from django.core.exceptions import ValidationError
from django.http import JsonResponse
import logging
import time


# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TransactionListCreateAPIView(ListCreateAPIView):
    queryset = FXTransaction.objects.all()
    serializer_class = FXTransactionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        customer_id = self.request.query_params.get('customer_id', None)
        if customer_id:
            cache_key = f"transactions_customer_{customer_id}"
            transactions = cache.get(cache_key)
            if transactions is None:
                transactions = list(FXTransaction.objects.filter(customer_id=customer_id).values())
                cache.set(cache_key, transactions, timeout=600)  # Cache for 10 minutes
                logger.info(f"Cache MISS for key: {cache_key}")
            else:
                logger.info(f"Cache HIT for key: {cache_key}")
            return transactions
        return super().get_queryset()

    def handle_error(self, message, status_code):
        logger.error(f"Error: {message}")
        return build_response(errors={"detail": message}, status_code=status_code, message=message)


class TransactionDetailAPIView(RetrieveAPIView):
    queryset = FXTransaction.objects.all()
    serializer_class = FXTransactionSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        cache_key = f"transaction_detail_{customer_id}"
        transactions = cache.get(cache_key)

        if transactions is None:
            transactions = FXTransaction.objects.filter(customer_id=customer_id)
            if not transactions.exists():
                message = "Transactions not found for the given customer_id."
                logger.warning(message)
                return build_response(errors={"detail": message}, status_code=status.HTTP_404_NOT_FOUND, message=message)
            serialized_data = self.get_serializer(transactions, many=True).data
            cache.set(cache_key, serialized_data, timeout=600)
        else:
            serialized_data = transactions

        logger.info(f"Transactions retrieved successfully for customer_id: {customer_id}")
        return build_response(data=serialized_data, message="Transactions successfully retrieved.")


# Currency Codes API View with Error Handling and Logging
class CurrencyCodesAPIView(GenericAPIView):
    serializer_class = CurrencyCodeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        cache_key = "currency_codes"
        start_time = time.time()
        currency_data = cache.get(cache_key)

        if currency_data is None:
            logger.info("Cache MISS for key: %s", cache_key)
            currency_data = get_currency_codes()
            if "error" not in currency_data:
                cache.set(cache_key, currency_data, timeout=86400)  # Cache for 1 day
            else:
                logger.error("Error fetching currency codes from external API.")
                return []  # Return an empty list if there is an error
        else:
            logger.info("Cache HIT for key: %s", cache_key)

        end_time = time.time()
        logger.info("Time taken to fetch data: %.2f seconds", end_time - start_time)
        return [{"code": currency} for currency in currency_data.get("currencies", [])]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            logger.warning("Failed to retrieve currency codes.")
            return build_response(errors={"detail": "Failed to retrieve currency codes."},
                                  status_code=status.HTTP_400_BAD_REQUEST,
                                  message="Error fetching currency codes.")
        serializer = self.get_serializer(data=queryset, many=True)
        serializer.is_valid()
        logger.info("Currency codes successfully retrieved and serialized.")
        return build_response(data=serializer.data, message="Currency codes retrieved successfully.")



class CurrencyConversionAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CurrencyConversionSerializer

    def post(self, request, *args, **kwargs):
        start_time = time.time()

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            message = "Invalid data"
            logger.error(message)
            return build_response(errors={"detail": message}, 
                                  status_code=status.HTTP_400_BAD_REQUEST,
                                  message="Invalid input data provided.")

        customer_id = serializer.validated_data['customer_id']
        input_amount = serializer.validated_data['input_amount']
        input_currency = serializer.validated_data['input_currency']
        output_currency = serializer.validated_data['output_currency']

        # Check if the user has set preferences
        try:
            user_preference = UserCurrencyPreference.objects.get(user=request.user)
        except UserCurrencyPreference.DoesNotExist:
            return build_response(errors={"detail": "User currency preferences not set."}, 
                                  status_code=status.HTTP_400_BAD_REQUEST,
                                  message="Please set your currency preferences first.")

        # Get the list of preferred pairs for the user
        preferred_pairs = user_preference.preferred_pairs.values_list('input_currency', 'output_currency')

        # Check if the chosen pair is in the user's preferences
        if (input_currency, output_currency) not in preferred_pairs:
            return build_response(errors={"detail": f"Currency pair {input_currency} to {output_currency} not found in your preferences."}, 
                                  status_code=status.HTTP_400_BAD_REQUEST,
                                  message="Please add this currency pair to your preferences.")

        # Fetch the conversion rate
        cache_key = f"conversion_{customer_id}_{input_currency}_{output_currency}_{input_amount}"
        conversion_data = cache.get(cache_key)

        if conversion_data is None:
            conversion_data = get_conversion_rate(input_currency, output_currency, input_amount)
            if "error" in conversion_data:
                logger.error(f"Error during currency conversion: {conversion_data}")
                return build_response(errors=conversion_data, 
                                      status_code=status.HTTP_400_BAD_REQUEST,
                                      message="Error during currency conversion.")
            cache.set(cache_key, conversion_data, timeout=600)
            logger.info(f"Cache MISS for {cache_key}. Data fetched from external service.")

            # Round the converted amount to the user's preferred decimal places
            converted_amount = round(conversion_data['converted_amount'], user_preference.decimal_places)

            response_data = {
                "customer_id": customer_id,
                "input_currency": input_currency,
                "output_currency": output_currency,
                "input_amount": input_amount,
                "output_amount": converted_amount,  # Rounded result
                "rate": conversion_data['rate']
            }
            return build_response(data=response_data, message="Conversion successful.")
        else:
            logger.info(f"Cache HIT for {cache_key}. Data served from cache.")
            converted_amount = round(conversion_data['converted_amount'], user_preference.decimal_places)

            response_data = {
                "customer_id": customer_id,
                "input_currency": input_currency,
                "output_currency": output_currency,
                "input_amount": input_amount,
                "output_amount": converted_amount,  # Rounded result
                "rate": conversion_data['rate']
            }
            return build_response(data=response_data, message="Data served from cache.")



@csrf_exempt  # Only for testing; remove in production
def list_cache_keys(request):
    # Get the Redis client
    redis_client = cache.client.get_client()

    # Fetch keys with a pattern (use '*' for all keys)
    keys = redis_client.keys('*')  # Adjust pattern if needed

    # Decode keys to strings
    decoded_keys = [key.decode('utf-8') for key in keys]

    # Return the keys as a JSON response
    return JsonResponse({'keys': decoded_keys})
