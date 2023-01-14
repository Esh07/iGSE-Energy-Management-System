# from app import User
# from . import User

# def get_user_by_email(email):
#     user = User.query.filter_by(email=email).first()
#     return user

# get all the EVC from the database and check if there is a match


def check_evc(evc):
    is_matched = False
    # get all the EVC from the database (table name: evc)
    evc_list = EVC.query.all()
    for evc in evc_list:
        if evc == evc:
            is_matched = True
            break
        else:
            is_matched = False
    return is_matched
