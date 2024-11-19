from django.urls import path
from .views import TransactionListCreateAPIView, TransactionDetailAPIView, CurrencyCodesAPIView, CurrencyConversionAPIView

urlpatterns = [
    path('api/transactions/', TransactionListCreateAPIView.as_view(), name='transaction-list-create'),
    path('api/transactions/customer/<str:customer_id>/', TransactionDetailAPIView.as_view(), name='transaction-detail-by-customer'),
    path('api/currencies/', CurrencyCodesAPIView.as_view(), name='currency-codes'),
    path('api/currency/convert/', CurrencyConversionAPIView.as_view(), name='currency-convert'),

]

