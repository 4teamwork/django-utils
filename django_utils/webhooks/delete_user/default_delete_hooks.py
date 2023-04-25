def inquire_delete(user):
    return (True, None)


def subscribe_delete(user):
    user.delete()
