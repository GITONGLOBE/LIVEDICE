class Profile:
    def __init__(self, user):
        self.user = user
        self.avatar = None
        self.banner = None
        self.bio = ""
        self.points = 0
        self.items = []

    def update_avatar(self, new_avatar):
        self.avatar = new_avatar

    def update_banner(self, new_banner):
        self.banner = new_banner

    def update_bio(self, new_bio):
        self.bio = new_bio

    def add_points(self, points):
        self.points += points

    def add_item(self, item):
        self.items.append(item)