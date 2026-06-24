
def api_response(success=True, data=None , message = ""):
    return ({
        "success":success,
        "message": message,
        "data":data
    })