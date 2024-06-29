from generic_game_logic_handler import GenericGameLogicHandler

def test_generic_game_logic_handler():
    handler = GenericGameLogicHandler()
    
    # Test initialization
    handler.initialize_game(3)
    assert len(handler.players) == 3
    assert handler.current_player == "Player 1"
    assert handler.game_state["round"] == 1
    assert handler.game_state["turn"] == 1
    
    # Test next_turn
    handler.next_turn()
    assert handler.current_player == "Player 2"
    assert handler.game_state["turn"] == 2
    
    # Test update_score
    handler.update_score("Player 1", 10)
    assert handler.game_state["scores"]["Player 1"] == 10
    
    # Test get_winner
    assert handler.get_winner() == "Player 1"
    
    # Test is_game_over
    assert not handler.is_game_over()
    
    print("All tests passed!")

if __name__ == "__main__":
    test_generic_game_logic_handler()