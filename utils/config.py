from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "utils"
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    APPROVAL_STATUS = ((APPROVED, APPROVED), (PENDING, PENDING), (REJECTED, REJECTED))

    ADD = "__add__"
    DELETE = "__delete__"
    UPDATE_INCREASE = "__update_increase__"
    UPDATE_DECREASE = "__update_decrease__"
    OPERATIONS = [ADD, DELETE, UPDATE_DECREASE, UPDATE_INCREASE]
