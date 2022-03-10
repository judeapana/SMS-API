class ErrorCodes:
    """
    >> system errors at authentication start with 9
    >> app errors start with 1 {unique values}
    >> system errors with transactions start with error code 5
    """
    EMAIL_TAKEN = {'code': "9001", 'description': 'Email already taken'}
    OTP_INVALID = {"code": "9002"}
    TOKEN_EXPIRED = {"code": "9003"}
    PHONE_NUMBER_INVALID = {"code": "9004"}
    UNAUTHORIZED = {"code": "9005"}
    PHONE_NUMBER_TAKEN = {"code": "9006"}
    UNIVERSITY_ALREADY_EXIST = {"code": "1001"}
    CAMPUS_ALREADY_EXIST = {"code": "1002"}
    USER_ALREADY_EXIST = {"code": "1003"}
    CONTACT_ALREADY_EXIST = {"code": "1004"}
    INVALID_AMOUNT = {"code": "5001"}
