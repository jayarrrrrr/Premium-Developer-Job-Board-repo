def effective_premium(request):
    """Expose a unified premium flag to templates: True if either User or Profile marks premium."""
    is_premium = False
    try:
        if getattr(request, 'user', None) and request.user.is_authenticated:
            profile = request.user.get_or_create_profile()
            is_premium = bool(getattr(profile, 'is_premium', False))
    except Exception:
        is_premium = False
    return {'effective_is_premium': bool(is_premium)}
