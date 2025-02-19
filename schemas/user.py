def userEntity(item) -> dict:
    return {
        "name":item["name"],
        "email":item["email"],
        "password":item["password"]
    }

def usersEntity(items) -> list:
    return [userEntity(item) for item in items]