from common.send_sms import send_sms


def get_queryset_for_current_site(model, request):
    """
    check current site domain
    :param request:
    :param model:
    :return: error if current site not equal to user site domain
    """
    return model.objects.get_queryset_for_current_site(request).all()


def send_invitation_message(user):
    import pdb; pdb.set_trace()
    body = 'Hi {name} ,\nYou have been added to {family} family ' \
           'Login to your family by clicking this link. \n' \
           '{subdomain}'.format(
            name=user.first_name if user.first_name else "Family User",
            family=user.family.name,
            subdomain=user.site.domain)
    send_sms(body, to_number=user.mobile)