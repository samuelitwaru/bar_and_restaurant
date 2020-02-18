class BaseConfig(object):
    'Base config class'
    SECRET_KEY = "A590LTGhyGRsXvcz25NNNVxfdJBxz359nF"


class ProductionConfig(BaseConfig):
    'Production specific config'
    DEBUG = False
    TESTING = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'samuelitwaru@gmail.com'
    MAIL_PASSWORD = 'helloitwaru'
    MAIL_DEFAULT_SENDER = 'samuelitwaru@gmail.com'


class DevelopmentConfig(BaseConfig):
    'Development environment specific config'
    # SECRET_KEY = "A590LTGhyGRsXvcz25NNNVxfdJBxz359nF"
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'samuelitwaru@gmail.com'
    MAIL_PASSWORD = 'helloitwaru'
    MAIL_DEFAULT_SENDER = 'samuelitwaru@gmail.com'
