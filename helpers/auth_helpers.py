from accounts.models import User



def create_user_account(
    identifier,
    password,
    role,
    organization=None,
    first_name=None
):

    user_data = {
        "email": None,
        "phone": None
    }

    if "@" in identifier:

        user_data["email"] = identifier

    else:

        user_data["phone"] = identifier

    user = User.objects.create_user(

        email=user_data["email"],

        phone=user_data["phone"],

        password=password,

        first_name=first_name,

        role=role,

        organization=organization,
        
        is_staff=role in ['SUPER_ADMIN', 'ORG_ADMIN']
    )

    return user