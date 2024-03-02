from pydantic import BaseModel, ValidationError
import json


class EmailInput(BaseModel):
    body: str


def parse_email_input(input_json: str):
    try:
        email_data = json.loads(input_json)
        email_input = EmailInput(**email_data)
        return email_input
    except ValidationError as e:
        print("Validation error when parsing EmailInput:", e)
        return None


class ApplyDiscount(BaseModel):
    task: str
    discount: float
    part_number: str


def parse_apply_discount_input(input_json: str, task: str):
    try:
        email_data = json.loads(input_json)
        email_input = ApplyDiscount(**email_data, task=task)
        return email_input
    except ValidationError as e:
        print("Validation error when parsing EmailInput:", e)
        return None