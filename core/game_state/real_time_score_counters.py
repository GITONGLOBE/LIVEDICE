class RealTimeScoreCounters:
    def __init__(self):
        self.game_state = None
        self.table_vscore = 0
        self.stash_vscore = 0
        self.stashstash_vscore = 0
        self.turn_vscore = 0
        self.stashselection_vscore = 0
        self.stashplusselection_vscore = 0
        self.stasheddice_var = 0
        self.rollcupdice_var = 6
        self.turn_nr_var = 0
        self.game_turns_var = 0
        self.stashstashtimes_vscore = 0
        self.turn_scorerecord = 0
        self.turn_rolls_var = 0
        self.turn_stashes_var = 0

    def update_counters(self, game_state):
        self.game_state = game_state
        self.table_vscore = game_state.referee.calculate_score(game_state.dice_values)
        self.stash_vscore = game_state.current_player.get_stash_score()
        self.stashstash_vscore = game_state.current_player.stash_stash
        self.turn_vscore = game_state.referee.calculate_turn_score()
        self.stashselection_vscore = game_state.referee.calculate_score([game_state.dice_values[i] for i in game_state.selected_dice])
        self.stashplusselection_vscore = self.stash_vscore + self.stashselection_vscore
        self.stasheddice_var = len(game_state.current_player.stashed_dice)
        self.rollcupdice_var = 6 - self.stasheddice_var
        self.turn_nr_var = game_state.current_player.turn_count + 1
        self.game_turns_var = game_state.get_game_turns()
        self.stashstashtimes_vscore = game_state.current_player.full_stashes_moved
        self.turn_scorerecord = self.turn_vscore
        self.turn_rolls_var = game_state.current_player.roll_count
        self.turn_stashes_var = game_state.current_player.stashes_this_turn

    def reset(self):
        self.table_vscore = 0
        self.stash_vscore = 0
        self.stashstash_vscore = 0
        self.turn_vscore = 0
        self.stashselection_vscore = 0
        self.stashplusselection_vscore = 0
        self.stasheddice_var = 0
        self.rollcupdice_var = 6
        self.turn_nr_var = 0
        self.game_turns_var = 0
        self.stashstashtimes_vscore = 0
        self.turn_scorerecord = 0
        self.turn_rolls_var = 0
        self.turn_stashes_var = 0