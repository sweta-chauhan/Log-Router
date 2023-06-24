from marshmallow import Schema, fields, validate

from log_router.constant.user_log import EVENT_NAME


class UserLogRequestSchema(Schema):
    id = fields.Integer(required=True)
    user_id = fields.Integer(required=True)
    unix_ts = fields.Integer(required=True)
    event_name = fields.String(required=True, validate=validate.OneOf(EVENT_NAME))


class UserLogSchema(Schema):
    uid = fields.String(primary_key=True)
    log_id = fields.Integer()
    unix_ts = fields.Integer()
    user_id = fields.Integer()
    event_name = fields.String()
