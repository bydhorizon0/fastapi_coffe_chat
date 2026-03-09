from fastapi import HTTPException, status


class DuplicatedEmail(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="중복된 계정 이메일입니다."
        )


class DuplicatedUsername(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="중복된 계정 ID입니다."
        )
