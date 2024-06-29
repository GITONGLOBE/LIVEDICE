class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password  # Note: In a real application, never store passwords in plain text
        self.handle = f"@{username}"  # LIVEDICE H@NDLE
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def activate(self):
        self.is_active = True

    def __str__(self):
        return f"User: {self.username} ({self.handle})"