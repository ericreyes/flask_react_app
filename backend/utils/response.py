from flask import jsonify

def success_response(data, message=None, meta=None, status_code=200):
    """
    Returns a success response in JSON format.

    Args:
        data (dict): The data to include in the response.
        message (str, optional): A message to include in the response. Defaults to None.
        meta (dict, optional): Metadata to include in the response. Defaults to None.
        status_code (int, optional): The HTTP status code for the response. Defaults to 200.

    Returns:
        tuple: A tuple containing the JSON response and the status code.
    """
    response = {
        "message": message,
        "status": "success",
    }
    if data is not None:
        response["data"] = data
    if meta is not None:
        response["meta"] = meta

    return jsonify(response), status_code

def error_response(error, message=None, status_code=500):
    """
    Returns an error response in JSON format.

    Args:
        error (str): The error message to include in the response.
        message (str, optional): A message to include in the response. Defaults to None.
        status_code (int, optional): The HTTP status code for the response. Defaults to 500.

    Returns:
        tuple: A tuple containing the JSON response and the status code.
    """
    response = {
        "message": message,
        "status": "error",
        "error": error,
    }
    return jsonify(response), status_code
