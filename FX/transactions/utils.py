from rest_framework.response import Response

def build_response(data=None, errors=None, status_code=200, message=None):
    """
    Utility function to build a standardized response for the API.
    """
    response = {
        "status": status_code,
        "message": message or "Success",
        "data": data or {},
        "errors": errors or {},
    }
    return Response(response, status=status_code)