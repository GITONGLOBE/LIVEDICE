# C:\LIVEDICE\ui\friend_list.py

class FriendListUI:
    def __init__(self, friend_system):
        self.friend_system = friend_system

    def display_friend_list(self, user_id):
        friends = self.friend_system.get_friend_list(user_id)
        # Implement UI logic to display friend list
        print(f"Displaying friend list for user {user_id}")
        for friend in friends:
            print(f"Friend: {friend['username']}, Status: {friend['status']}")

    def send_friend_request_ui(self, sender_id):
        # Implement UI logic for sending friend requests
        receiver_id = input("Enter the user ID of the friend you want to add: ")
        if self.friend_system.send_friend_request(sender_id, receiver_id):
            print("Friend request sent successfully")
        else:
            print("Failed to send friend request")

    def handle_friend_request_ui(self, receiver_id):
        # Implement UI logic for handling incoming friend requests
        sender_id = input("Enter the user ID of the friend request you want to accept: ")
        if self.friend_system.accept_friend_request(sender_id, receiver_id):
            print("Friend request accepted")
        else:
            print("Failed to accept friend request")

    def search_friends_ui(self, user_id):
        # Implement UI logic for searching friends
        query = input("Enter a username to search for: ")
        results = self.friend_system.search_friends(user_id, query)
        print(f"Search results for '{query}':")
        for friend in results:
            print(f"Friend: {friend['username']}, Status: {friend['status']}")

# Add a main function for testing
def main():
    from core.friend_system import FriendSystem
    from core.user_management import UserManager
    
    user_manager = UserManager()
    friend_system = FriendSystem(user_manager)
    ui = FriendListUI(friend_system)
    
    # Add some test users
    user_manager.create_user("user1", "alice@example.com", "password")
    user_manager.create_user("user2", "bob@example.com", "password")
    user_manager.create_user("user3", "charlie@example.com", "password")
    
    # Test the UI functions
    ui.send_friend_request_ui("user1")
    ui.handle_friend_request_ui("user2")
    ui.display_friend_list("user1")
    ui.search_friends_ui("user1")

if __name__ == "__main__":
    main()