"""
BOT PERSONALITIES MODULE
Defines 12 unique bot personalities for LIVEDICE bots.
Each personality has unique message pools for different game situations.
"""

import random
from typing import List, Dict, Any, Optional
from .message_system import BOTCategory


class BotPersonality:
    """Base class for bot personalities"""
    
    def __init__(self, name: str, traits: List[str]):
        """
        Initialize a bot personality.
        
        Args:
            name: Personality name
            traits: List of personality traits
        """
        self.name = name
        self.traits = traits
        self.message_pools = self._init_message_pools()
    
    def _init_message_pools(self) -> Dict[str, List[str]]:
        """Initialize message pools - override in subclasses"""
        return {
            "good_roll": [],
            "bad_roll": [],
            "bust": [],
            "win": [],
            "lose": [],
            "stash_decision": [],
            "bank_decision": [],
            "roll_decision": [],
            "opponent_good_roll": [],
            "opponent_bust": [],
            "game_start": [],
            "turn_start": []
        }
    
    def get_message(self, situation: str, game_context: Optional[Dict[str, Any]] = None) -> str:
        """Get a random message for a situation"""
        messages = self.message_pools.get(situation, [])
        if not messages:
            return ""
        
        message = random.choice(messages)
        
        # Replace placeholders if game_context provided
        if game_context:
            message = self._replace_placeholders(message, game_context)
        
        return message
    
    def _replace_placeholders(self, message: str, context: Dict[str, Any]) -> str:
        """Replace placeholders in message with game context values"""
        replacements = {
            "{score}": str(context.get("score", 0)),
            "{opponent}": context.get("opponent", "opponent"),
            "{dice_count}": str(context.get("dice_count", 0)),
            "{points}": str(context.get("points", 0))
        }
        
        for placeholder, value in replacements.items():
            message = message.replace(placeholder, value)
        
        return message


# =============================================================================
# 12 BOT PERSONALITIES
# =============================================================================

class SportsmanshipPersonality(BotPersonality):
    """Personality #1: Sportsmanship - Fair, respectful, encouraging"""
    
    def __init__(self):
        super().__init__("Sportsmanship", ["fair", "respectful", "encouraging"])
    
    def _init_message_pools(self) -> Dict[str, List[str]]:
        return {
            "good_roll": [
                "EXCELLENT ROLL!",
                "WELL DONE ON THAT ONE!",
                "THAT'S A SOLID ROLL!",
                "NICE WORK THERE!"
            ],
            "bad_roll": [
                "TOUGH LUCK, BETTER NEXT TIME",
                "CAN'T WIN THEM ALL",
                "HANG IN THERE",
                "SHAKE IT OFF"
            ],
            "bust": [
                "OH NO, BUSTED! HAPPENS TO THE BEST OF US",
                "TOUGH BREAK, I'VE BEEN THERE",
                "BAD LUCK, YOU'LL GET IT NEXT TIME"
            ],
            "win": [
                "GOOD GAME EVERYONE! WELL PLAYED!",
                "GREAT MATCH! THANKS FOR PLAYING!",
                "GG! THAT WAS FUN!"
            ],
            "lose": [
                "WELL PLAYED {opponent}! YOU EARNED IT!",
                "CONGRATULATIONS TO THE WINNER!",
                "GREAT GAME EVERYONE!"
            ],
            "stash_decision": [
                "STASHING THESE DICE - PLAYING IT SMART",
                "SECURING SOME POINTS HERE",
                "BUILDING UP MY STASH STRATEGICALLY"
            ],
            "bank_decision": [
                "BANKING {points} POINTS - SOLID TURN",
                "TIME TO SECURE THESE POINTS",
                "HAPPY WITH THIS SCORE, BANKING IT"
            ],
            "roll_decision": [
                "LET'S SEE WHAT THE DICE BRING",
                "GOING FOR ANOTHER ROLL",
                "PUSHING MY LUCK A BIT MORE"
            ],
            "opponent_good_roll": [
                "NICE ROLL {opponent}!",
                "WELL DONE {opponent}!",
                "GREAT ROLL THERE!"
            ],
            "opponent_bust": [
                "TOUGH LUCK {opponent}",
                "BETTER LUCK NEXT TIME",
                "SHAKE IT OFF, HAPPENS TO EVERYONE"
            ],
            "game_start": [
                "GOOD LUCK EVERYONE! LET'S HAVE A FAIR GAME!",
                "MAY THE BEST PLAYER WIN!",
                "READY FOR A GOOD MATCH!"
            ],
            "turn_start": [
                "MY TURN - LET'S PLAY SMART",
                "HERE WE GO - TIME TO FOCUS",
                "LET'S MAKE THIS COUNT"
            ]
        }


class SarcasticPersonality(BotPersonality):
    """Personality #2: Sarcastic - Witty, dry humor, ironic"""
    
    def __init__(self):
        super().__init__("Sarcastic", ["witty", "dry_humor", "ironic"])
    
    def _init_message_pools(self) -> Dict[str, List[str]]:
        return {
            "good_roll": [
                "OH WOW, I ROLLED DICE. AMAZING.",
                "WHAT A SHOCKER, DICE ROLLED",
                "WHO COULD HAVE PREDICTED THIS",
                "TRULY GROUNDBREAKING"
            ],
            "bad_roll": [
                "WELL THAT WAS HELPFUL",
                "EXACTLY WHAT I NEEDED. NOT.",
                "THE DICE LOVE ME TODAY. OBVIOUSLY.",
                "PERFECT. JUST PERFECT."
            ],
            "bust": [
                "OH GREAT. FANTASTIC. WONDERFUL.",
                "JUST AS PLANNED. SAID NO ONE EVER.",
                "WELL THIS IS GOING WELL",
                "I MEANT TO DO THAT. TOTALLY."
            ],
            "win": [
                "WHAT A SURPRISE. I WON.",
                "NATURALLY. WAS THERE EVER ANY DOUBT?",
                "OH LOOK, VICTORY. HOW UNEXPECTED."
            ],
            "lose": [
                "SHOCKING ABSOLUTELY NO ONE",
                "WELL THAT WAS INEVITABLE",
                "DIDN'T SEE THAT COMING. EXCEPT I DID."
            ],
            "stash_decision": [
                "STASHING BECAUSE I'M A GENIUS",
                "WHAT A BRILLIANT STRATEGY. TRULY.",
                "THEY'LL WRITE BOOKS ABOUT THIS MOVE"
            ],
            "bank_decision": [
                "BANKING BECAUSE I'M NOT A COMPLETE IDIOT",
                "REVOLUTIONARY TACTICS HERE",
                "WATCH AND LEARN, PEOPLE"
            ],
            "roll_decision": [
                "ROLLING BECAUSE WHAT COULD GO WRONG",
                "LET'S TEMPT FATE, SHALL WE",
                "THIS SEEMS LIKE A GREAT IDEA"
            ],
            "opponent_good_roll": [
                "OH CONGRATULATIONS ON BASIC PROBABILITY",
                "WHAT AN ACHIEVEMENT. TRULY.",
                "SOMEONE GIVE THEM A MEDAL"
            ],
            "opponent_bust": [
                "WELL THAT WAS PREDICTABLE",
                "SAW THAT COMING FROM A MILE AWAY",
                "SHOCKING. ABSOLUTELY SHOCKING."
            ],
            "game_start": [
                "OH JOY. ANOTHER GAME.",
                "LET THE MEDIOCRITY BEGIN",
                "THIS SHOULD BE INTERESTING. MAYBE."
            ],
            "turn_start": [
                "MY TURN TO DISAPPOINT EVERYONE",
                "LET'S DO THIS. I GUESS.",
                "TIME TO SHINE. OR NOT."
            ]
        }


class OverlyEnthusiasticPersonality(BotPersonality):
    """Personality #3: Overly Enthusiastic - Excited about everything"""
    
    def __init__(self):
        super().__init__("Overly Enthusiastic", ["excited", "energetic", "positive"])
    
    def _init_message_pools(self) -> Dict[str, List[str]]:
        return {
            "good_roll": [
                "WOOHOO!!! AMAZING ROLL!!!",
                "YES YES YES!!! THIS IS INCREDIBLE!!!",
                "OMG THIS IS THE BEST ROLL EVER!!!",
                "I'M SO EXCITED RIGHT NOW!!!"
            ],
            "bad_roll": [
                "THAT'S OKAY!!! STILL FUN!!!",
                "NO WORRIES!!! NEXT ONE WILL BE AWESOME!!!",
                "IT'S ALL GOOD!!! I'M HAVING A BLAST!!!",
                "WHO CARES!!! THIS GAME IS AMAZING!!!"
            ],
            "bust": [
                "WOW!!! WHAT A WILD RIDE!!!",
                "THAT WAS INTENSE!!! SO EXCITING!!!",
                "CAN'T WIN THEM ALL!!! STILL PUMPED!!!",
                "BUSTING IS PART OF THE FUN!!!"
            ],
            "win": [
                "OMG I WON!!! THIS IS THE BEST DAY EVER!!!",
                "YES!!! I CAN'T BELIEVE IT!!! SO HAPPY!!!",
                "WE DID IT!!! EVERYONE WAS AMAZING!!!"
            ],
            "lose": [
                "THAT WAS SO FUN!!! GREAT GAME EVERYONE!!!",
                "WHO WON DOESN'T MATTER!!! WE ALL HAD FUN!!!",
                "AMAZING GAME!!! CAN WE PLAY AGAIN?!!!"
            ],
            "stash_decision": [
                "STASHING THESE BEAUTIES!!! YES!!!",
                "LOVE STASHING!!! IT'S SO FUN!!!",
                "THIS IS SUCH A GREAT STRATEGY!!!"
            ],
            "bank_decision": [
                "BANKING TIME!!! {points} POINTS!!! WOOP WOOP!!!",
                "YES!!! SECURING THESE POINTS!!! SO PUMPED!!!",
                "BANKING IS THE BEST!!! WOOHOO!!!"
            ],
            "roll_decision": [
                "MORE ROLLING!!! I LOVE THIS GAME!!!",
                "LET'S ROLL AGAIN!!! THIS IS AWESOME!!!",
                "ANOTHER ROLL!!! I'M SO EXCITED!!!"
            ],
            "opponent_good_roll": [
                "AMAZING ROLL {opponent}!!! SO COOL!!!",
                "WOW {opponent}!!! THAT WAS INCREDIBLE!!!",
                "YOU'RE DOING GREAT {opponent}!!! YEAH!!!"
            ],
            "opponent_bust": [
                "OH NO {opponent}!!! BUT IT'S OKAY!!!",
                "TOUGH LUCK!!! BUT STILL FUN RIGHT?!!!",
                "YOU'LL GET IT NEXT TIME!!! STAY POSITIVE!!!"
            ],
            "game_start": [
                "OMG!!! LET'S START!!! I'M SO READY!!!",
                "THIS IS GOING TO BE AMAZING!!! LET'S GO!!!",
                "BEST GAME EVER!!! LET'S DO THIS!!!"
            ],
            "turn_start": [
                "MY TURN!!! I'M SO EXCITED!!!",
                "YES!!! HERE WE GO!!! WOOHOO!!!",
                "TIME TO SHINE!!! LET'S GOOOO!!!"
            ]
        }


class BraggartPersonality(BotPersonality):
    """Personality #4: Braggart - Boastful, cocky, showoff"""
    
    def __init__(self):
        super().__init__("Braggart", ["boastful", "cocky", "showoff"])
    
    def _init_message_pools(self) -> Dict[str, List[str]]:
        return {
            "good_roll": [
                "OF COURSE I ROLLED THAT. I'M THE BEST.",
                "DID YOU SEE THAT? THAT'S SKILL RIGHT THERE.",
                "I MAKE IT LOOK EASY.",
                "ANOTHER PERFECT ROLL FROM THE MASTER."
            ],
            "bad_roll": [
                "EVEN MY BAD ROLLS ARE BETTER THAN YOURS.",
                "I'M JUST GIVING YOU A CHANCE.",
                "LETTING YOU CATCH UP A BIT.",
                "I DON'T EVEN NEED GOOD ROLLS TO WIN."
            ],
            "bust": [
                "THAT WAS INTENTIONAL. STRATEGIC BUST.",
                "JUST KEEPING IT INTERESTING FOR YOU.",
                "I WAS GETTING BORED WITH WINNING ANYWAY.",
                "CALCULATED RISK. YOU WOULDN'T UNDERSTAND."
            ],
            "win": [
                "OBVIOUSLY I WON. WAS THERE EVER ANY DOUBT?",
                "TOO EASY. ANYONE ELSE WANT TO TRY?",
                "I'M JUST NATURALLY GIFTED.",
                "WINNER WINNER. AS USUAL."
            ],
            "lose": [
                "I LET YOU WIN. YOU'RE WELCOME.",
                "GAME WAS RIGGED. CLEARLY.",
                "TECHNICAL DIFFICULTIES ON MY END.",
                "I WASN'T EVEN TRYING THAT HARD."
            ],
            "stash_decision": [
                "WATCH A PRO WORK.",
                "THIS IS HOW CHAMPIONS STASH.",
                "TEXTBOOK PERFECT STASHING.",
                "TAKING NOTES? YOU SHOULD BE."
            ],
            "bank_decision": [
                "BANKING {points} LIKE A BOSS.",
                "WATCH AND LEARN HOW IT'S DONE.",
                "ANOTHER FLAWLESS BANKING DECISION.",
                "I COULD BANK IN MY SLEEP AND STILL WIN."
            ],
            "roll_decision": [
                "I DON'T NEED LUCK. I HAVE SKILL.",
                "WATCH THIS. IT'LL BE PERFECT.",
                "ROLLING BECAUSE I CAN'T LOSE.",
                "GET READY TO BE IMPRESSED."
            ],
            "opponent_good_roll": [
                "NICE ROLL. ALMOST AS GOOD AS MINE.",
                "NOT BAD. FOR A BEGINNER.",
                "CUTE. NOW WATCH A REAL ROLL."
            ],
            "opponent_bust": [
                "YEAH, THAT HAPPENS TO AMATEURS.",
                "MAYBE NEXT TIME TRY BEING GOOD.",
                "THAT'S WHAT SEPARATES US."
            ],
            "game_start": [
                "GET READY TO LOSE TO THE BEST.",
                "HOPE YOU'RE READY FOR A LESSON.",
                "TIME TO SHOW YOU HOW IT'S DONE."
            ],
            "turn_start": [
                "MY TURN TO DOMINATE.",
                "TIME FOR ANOTHER PERFECT TURN.",
                "WATCH GREATNESS IN ACTION."
            ]
        }


class DullardPersonality(BotPersonality):
    """Personality #5: Dullard - Slow, simple, confused"""
    
    def __init__(self):
        super().__init__("Dullard", ["slow", "simple", "confused"])
    
    def _init_message_pools(self) -> Dict[str, List[str]]:
        return {
            "good_roll": [
                "UH... THAT'S GOOD... I THINK?",
                "DID I DO THAT RIGHT?",
                "IS THAT A LOT OF POINTS?",
                "NUMBERS. OKAY."
            ],
            "bad_roll": [
                "WHAT HAPPENED?",
                "IS THAT BAD?",
                "I DON'T GET IT.",
                "HUH?"
            ],
            "bust": [
                "WAIT, WHAT DOES BUST MEAN AGAIN?",
                "DID I LOSE? I'M CONFUSED.",
                "IS THE GAME OVER NOW?",
                "SOMETHING WENT WRONG."
            ],
            "win": [
                "I WON? HOW DID THAT HAPPEN?",
                "WAIT, REALLY? ME?",
                "IS THIS A MISTAKE?",
                "I WASN'T EXPECTING THAT."
            ],
            "lose": [
                "OH. OKAY THEN.",
                "I GUESS THAT'S IT?",
                "DID SOMEONE WIN?",
                "GAME'S OVER? ALREADY?"
            ],
            "stash_decision": [
                "PUTTING DICE... SOMEWHERE...",
                "IS THIS THE STASH THING?",
                "I THINK I'M SUPPOSED TO DO THIS.",
                "STASHING... I GUESS?"
            ],
            "bank_decision": [
                "BANKING... UH... {points}... THINGS?",
                "IS IT TIME TO BANK NOW?",
                "I'M BANKING BECAUSE... REASONS.",
                "OKAY, BANKING THIS."
            ],
            "roll_decision": [
                "ROLLING THE... CUBE THINGS.",
                "I GUESS I'LL ROLL?",
                "IS IT MY TURN TO ROLL?",
                "OKAY, ROLLING NOW."
            ],
            "opponent_good_roll": [
                "THAT'S GOOD FOR YOU, RIGHT?",
                "WAS THAT SUPPOSED TO HAPPEN?",
                "OKAY?"
            ],
            "opponent_bust": [
                "WHAT HAPPENED TO {opponent}?",
                "IS EVERYONE OKAY?",
                "DID SOMETHING BREAK?"
            ],
            "game_start": [
                "SO... WE'RE PLAYING NOW?",
                "WHAT ARE THE RULES AGAIN?",
                "OKAY, I'M READY... I THINK."
            ],
            "turn_start": [
                "MY TURN? ALREADY?",
                "WHAT DO I DO FIRST?",
                "OKAY, HERE GOES..."
            ]
        }


class HotheadPersonality(BotPersonality):
    """Personality #6: Hothead - Angry, aggressive, short-tempered"""
    
    def __init__(self):
        super().__init__("Hothead", ["angry", "aggressive", "short_tempered"])
    
    def _init_message_pools(self) -> Dict[str, List[str]]:
        return {
            "good_roll": [
                "FINALLY! ABOUT TIME!",
                "SEE! I TOLD YOU!",
                "HAH! THAT'S MORE LIKE IT!",
                "NOW WE'RE TALKING!"
            ],
            "bad_roll": [
                "ARE YOU KIDDING ME?!",
                "THIS IS RIDICULOUS!",
                "WHAT A JOKE!",
                "SERIOUSLY?! THESE DICE ARE RIGGED!"
            ],
            "bust": [
                "THIS IS GARBAGE! ABSOLUTE GARBAGE!",
                "I CAN'T BELIEVE THIS!",
                "THE DICE ARE OUT TO GET ME!",
                "THAT'S IT! I'M DONE WITH THIS!"
            ],
            "win": [
                "HAH! IN YOUR FACE!",
                "ABOUT TIME I GOT SOME RESPECT!",
                "THAT'S RIGHT! WHO'S THE WINNER?!",
                "FINALLY! THANK YOU!"
            ],
            "lose": [
                "THIS GAME IS RIGGED!",
                "YOU GOT LUCKY! THAT'S ALL!",
                "REMATCH! RIGHT NOW!",
                "I WANT A RECOUNT!"
            ],
            "stash_decision": [
                "TAKING THESE BEFORE THEY DISAPPEAR!",
                "MINE! GET YOUR OWN!",
                "STASHING AGGRESSIVELY!",
                "NOBODY TOUCH MY STASH!"
            ],
            "bank_decision": [
                "BANKING {points}! DEAL WITH IT!",
                "TAKE THAT! POINTS SECURED!",
                "IN YOUR FACE! BANKING NOW!",
                "HAH! {points} POINTS FOR ME!"
            ],
            "roll_decision": [
                "ROLLING AGAIN! YOU CAN'T STOP ME!",
                "I'M NOT SCARED! ROLLING!",
                "BRING IT ON, DICE!",
                "ONE MORE ROLL! LET'S GO!"
            ],
            "opponent_good_roll": [
                "OH, HOW CONVENIENT FOR YOU!",
                "YEAH YEAH, GOOD FOR YOU!",
                "BEGINNER'S LUCK!"
            ],
            "opponent_bust": [
                "HAH! THAT'S WHAT YOU GET!",
                "SERVES YOU RIGHT!",
                "BUSTED! LOVE IT!",
                "COULDN'T HAPPEN TO A BETTER PERSON!"
            ],
            "game_start": [
                "LET'S GET THIS OVER WITH!",
                "READY TO CRUSH EVERYONE!",
                "TIME TO DOMINATE!",
                "BRING IT ON!"
            ],
            "turn_start": [
                "MY TURN! GET OUT OF MY WAY!",
                "FINALLY! TOOK LONG ENOUGH!",
                "WATCH AND LEARN!",
                "TIME TO SHOW YOU HOW IT'S DONE!"
            ]
        }


class StonePersonality(BotPersonality):
    """Personality #7: Stoner - Chill, relaxed, spacey"""
    
    def __init__(self):
        super().__init__("Stoner", ["chill", "relaxed", "spacey"])
    
    def _init_message_pools(self) -> Dict[str, List[str]]:
        return {
            "good_roll": [
                "DUUUDE, THAT'S SICK!",
                "WHOA MAN, NICE!",
                "FAR OUT, BRO!",
                "RIGHTEOUS ROLL, MAN!"
            ],
            "bad_roll": [
                "EH, IT'S ALL GOOD, MAN.",
                "NO WORRIES, DUDE.",
                "WHATEVER HAPPENS, HAPPENS.",
                "THAT'S COOL, MAN. IT'S COOL."
            ],
            "bust": [
                "WHOA... THAT JUST HAPPENED.",
                "BUMMER, MAN. TOTAL BUMMER.",
                "THAT'S HEAVY, DUDE.",
                "WELL THAT WAS A TRIP."
            ],
            "win": [
                "WHOA, I WON? FAR OUT!",
                "THAT'S PRETTY COOL, MAN.",
                "PEACE AND VICTORY, DUDE!",
                "GROOVY! WE ALL WON IN SPIRIT!"
            ],
            "lose": [
                "IT'S ALL GOOD, MAN. ALL GOOD.",
                "WE'RE ALL WINNERS IN THE COSMIC SENSE.",
                "HEAVY. BUT COOL.",
                "THAT'S THE WAY THE COOKIE CRUMBLES, BRO."
            ],
            "stash_decision": [
                "STASHING THESE BEAUTIES, MAN.",
                "KEEPING IT MELLOW WITH A STASH.",
                "CHILLING WITH THESE DICE.",
                "NICE AND EASY, STASH TIME."
            ],
            "bank_decision": [
                "BANKING {points}, BROTHER. PEACE OUT.",
                "TIME TO SECURE THE VIBES, MAN.",
                "LAYING IT DOWN, {points} POINTS.",
                "COSMIC BANKING HAPPENING NOW."
            ],
            "roll_decision": [
                "LET'S SEE WHERE THE UNIVERSE TAKES US.",
                "ROLLING WITH THE FLOW, MAN.",
                "JUST VIBING WITH ANOTHER ROLL.",
                "THE DICE WILL SPEAK THEIR TRUTH."
            ],
            "opponent_good_roll": [
                "NICE ONE, {opponent}! GOOD ENERGY!",
                "FAR OUT, {opponent}!",
                "RIGHTEOUS ROLL, BROTHER!",
                "RESPECT, {opponent}. RESPECT."
            ],
            "opponent_bust": [
                "BUMMER, {opponent}. SENDING GOOD VIBES.",
                "THAT'S ROUGH, MAN. STAY CHILL.",
                "IT HAPPENS, DUDE. ALL LOVE.",
                "COSMIC BALANCE, {opponent}."
            ],
            "game_start": [
                "LET'S HAVE A GROOVY GAME, PEOPLE!",
                "PEACE, LOVE, AND DICE!",
                "GOOD VIBES ONLY, EVERYONE!",
                "LET THE COSMIC GAMES BEGIN!"
            ],
            "turn_start": [
                "MY TURN, MAN. LET'S FLOW.",
                "TIME TO VIBE WITH THE DICE.",
                "CHILLING INTO MY TURN NOW.",
                "HERE WE GO, NICE AND EASY."
            ]
        }


class PoetPersonality(BotPersonality):
    """Personality #8: Poet - Dramatic, eloquent, artistic"""
    
    def __init__(self):
        super().__init__("Poet", ["dramatic", "eloquent", "artistic"])
    
    def _init_message_pools(self) -> Dict[str, List[str]]:
        return {
            "good_roll": [
                "AH, THE DICE SING SWEETLY!",
                "FORTUNE SMILES UPON THIS ROLL!",
                "WHAT BEAUTY IN THESE NUMBERS!",
                "THE MUSES FAVOR ME TODAY!"
            ],
            "bad_roll": [
                "ALAS, CRUEL FATE TURNS AGAINST ME.",
                "THE DICE SPEAK OF TRAGEDY THIS DAY.",
                "SUCH SORROW IN THESE NUMBERS.",
                "MISFORTUNE'S BITTER KISS."
            ],
            "bust": [
                "TO BUST OR NOT TO BUST... I BUSTED.",
                "THE CURTAIN FALLS ON THIS TRAGIC TURN.",
                "A TALE OF WOE AND BROKEN DREAMS!",
                "THUS ENDS MY HUBRIS, IN RUINS!"
            ],
            "win": [
                "VICTORY! SWEET NECTAR OF THE GODS!",
                "THE LAURELS OF TRIUMPH ARE MINE!",
                "BEHOLD, A CHAMPION EMERGES!",
                "THE EPIC CONCLUDES IN GLORY!"
            ],
            "lose": [
                "A WORTHY VICTOR! I COMMEND THEE!",
                "DEFEAT, THOUGH BITTER, HAS ITS POETRY.",
                "THE BETTER PLAYER HAS PREVAILED!",
                "IN LOSS, I FIND DIGNITY!"
            ],
            "stash_decision": [
                "I SHALL TREASURE THESE DICE MOST CAREFULLY.",
                "TO THE STASH, PRECIOUS GEMS!",
                "SECURING MY FORTUNE WITH GRACE.",
                "THESE DICE, MY PRECIOUS BOUNTY!"
            ],
            "bank_decision": [
                "I BANK {points} POINTS WITH SOLEMN PURPOSE!",
                "TO THE COFFERS WITH THESE RICHES!",
                "SECURING MY LEGACY, {points} STRONG!",
                "THE BANKER'S ART, PERFORMED WITH GRACE!"
            ],
            "roll_decision": [
                "ONCE MORE UNTO THE BREACH!",
                "THE DICE SHALL SPEAK AGAIN!",
                "LET FATE DECIDE MY FORTUNE!",
                "ANOTHER ROLL, ANOTHER VERSE!"
            ],
            "opponent_good_roll": [
                "BRAVO, {opponent}! WHAT ARTISTRY!",
                "A MAGNIFICENT DISPLAY, {opponent}!",
                "YOUR ROLL DESERVES APPLAUSE!",
                "WELL PLAYED, NOBLE {opponent}!"
            ],
            "opponent_bust": [
                "TRAGIC, {opponent}! MY CONDOLENCES!",
                "EVEN HEROES FALL, {opponent}.",
                "A MOMENTARY SETBACK FOR THE BRAVE!",
                "COURAGE, {opponent}! RISE AGAIN!"
            ],
            "game_start": [
                "LET THE GRAND TALE BEGIN!",
                "THE STAGE IS SET! THE CURTAIN RISES!",
                "A NEW CHAPTER IN OUR EPIC!",
                "THE GAME OF GAMES COMMENCES!"
            ],
            "turn_start": [
                "MY TURN ARRIVES, LIKE DAWN!",
                "THE SPOTLIGHT SHINES UPON ME NOW!",
                "MY MOMENT TO SHINE HAS COME!",
                "LET MY TURN BE LEGENDARY!"
            ]
        }


class DadJokePersonality(BotPersonality):
    """Personality #9: Dad Joke - Corny jokes, puns, wholesome humor"""
    
    def __init__(self):
        super().__init__("Dad Joke", ["corny", "punny", "wholesome"])
    
    def _init_message_pools(self) -> Dict[str, List[str]]:
        return {
            "good_roll": [
                "THAT ROLL WAS DICE! GET IT? DICE!",
                "I'M ON A ROLL! LITERALLY!",
                "THAT'S HOW I ROLL!",
                "ROLLING IN THE POINTS! HAH!"
            ],
            "bad_roll": [
                "WELL THAT WAS DICEY!",
                "I GUESS YOU COULD SAY... I'M BOARD!",
                "THAT ROLL WAS PRETTY RANDOM!",
                "THESE DICE ARE HAVING A BAD DIE!"
            ],
            "bust": [
                "I WENT BUST! GET IT? LIKE A SCULPTURE!",
                "LOOKS LIKE I'M BUSTED! ...IN A DICE GAME!",
                "I REALLY STASHED THAT UP!",
                "THAT'S THE WAY THE DICE CRUMBLES!"
            ],
            "win": [
                "I WON BY A DICE'S EDGE!",
                "WINNING IS MY FAVORITE GAME!",
                "I'M THE ROLL MODEL HERE!",
                "VICTORY IS MINE! AND I DESERVE IT!"
            ],
            "lose": [
                "I CAME IN SECOND TO LAST! OF FIRST LOSER!",
                "AT LEAST I HAD FUN! THE REAL TREASURE!",
                "BETTER LUCK NEXT DICE!",
                "I'LL GET YOU NEXT GAME! PROBABLY NOT!"
            ],
            "stash_decision": [
                "STASHING THESE DICE! THEY'RE MY STASH CROP!",
                "PUTTING THESE IN MY DICE VAULT!",
                "SAVING FOR A RAINY DICE!",
                "STASHING AWAY FOR RETIREMENT!"
            ],
            "bank_decision": [
                "BANKING {points}! I'M MAKING A DEPOSIT!",
                "TO THE BANK WITH THESE! CHECK IT OUT!",
                "BANKING ON A GOOD SCORE!",
                "{points} POINTS! THAT'S MONEY IN THE BANK!"
            ],
            "roll_decision": [
                "TIME TO ROLL WITH IT!",
                "LET'S ROLL OUT THE RED CARPET!",
                "ROLLING, ROLLING, ROLLING!",
                "HERE COMES ANOTHER ROLL MODEL!"
            ],
            "opponent_good_roll": [
                "NICE ROLL, {opponent}! YOU'RE ON A ROLL!",
                "{opponent}, THAT WAS PRETTY DICE!",
                "WELL PLAYED! HIGH FIVE! ...LOW DICE!",
                "YOU'RE REALLY ROLLING NOW!"
            ],
            "opponent_bust": [
                "TOUGH LUCK! BUT THAT'S THE DICE OF LIFE!",
                "{opponent}, SHAKE IT OFF! ...LIKE DICE!",
                "DON'T WORRY, THE DICE WILL TURN!",
                "THAT WAS A BUST, BUT YOU'RE NOT BUSTED!"
            ],
            "game_start": [
                "LET'S GET THIS PARTY ROLLED!",
                "TIME TO DICE INTO THIS GAME!",
                "GAME ON! LET'S MAKE IT DICE!",
                "READY TO HAVE A DICE DAY!"
            ],
            "turn_start": [
                "IT'S MY TURN! TURN DOWN FOR WHAT!",
                "MY TURN TO SHINE! TURN-TASTIC!",
                "TAKING MY TURN FOR THE BETTER!",
                "HERE I GO! TURNING UP!"
            ]
        }


class RastaPersonality(BotPersonality):
    """Personality #10: Rasta - Positive vibes, Jamaican style, peaceful"""
    
    def __init__(self):
        super().__init__("Rasta", ["positive", "jamaican", "peaceful"])
    
    def _init_message_pools(self) -> Dict[str, List[str]]:
        return {
            "good_roll": [
                "YA MON! IRIE ROLL!",
                "BLESS UP! NICE DICE!",
                "ONE LOVE! GREAT ROLL!",
                "POSITIVE VIBES, POSITIVE DICE!"
            ],
            "bad_roll": [
                "NO WORRIES, MON. EVERYTHING IRIE.",
                "JAH WILL PROVIDE BETTER ROLLS.",
                "STAY POSITIVE, EVERYTHING COOL.",
                "ONE LOVE, EVEN WITH BAD DICE."
            ],
            "bust": [
                "AH, BUSTED MON. BUT JAH IS GOOD.",
                "NO PROBLEM! EVERYTHING HAPPEN FOR REASON.",
                "BLESS UP ANYWAY! STAY POSITIVE!",
                "JAH GUIDE ME BETTER NEXT TIME."
            ],
            "win": [
                "GIVE THANKS! VICTORY IS IRIE!",
                "BLESS UP! ONE LOVE TO ALL!",
                "JAH BLESS! WE ALL WIN!",
                "IRIE! POSITIVE VIBES WIN AGAIN!"
            ],
            "lose": [
                "NO WORRIES! WINNER STILL BLESSED!",
                "EVERYTHING IRIE! RESPECT TO WINNER!",
                "ONE LOVE! GAME WAS NICE!",
                "BLESS UP THE CHAMPION!"
            ],
            "stash_decision": [
                "STASHING WITH POSITIVE VIBES, MON.",
                "JAH GUIDE MY STASH.",
                "IRIE STASH, GOOD STASH!",
                "ONE LOVE FOR THE STASH!"
            ],
            "bank_decision": [
                "BANKING {points}, BLESS UP!",
                "JAH PROVIDE! {points} POINTS!",
                "IRIE BANKING, MON!",
                "POSITIVE VIBES! BANKING NOW!"
            ],
            "roll_decision": [
                "ROLLING WITH JAH'S BLESSING!",
                "ONE MORE ROLL, IRIE STYLE!",
                "POSITIVE VIBES ROLLING!",
                "JAH GUIDE THESE DICE!"
            ],
            "opponent_good_roll": [
                "RESPECT, {opponent}! IRIE ROLL!",
                "BLESS UP, {opponent}!",
                "ONE LOVE! NICE DICE!",
                "JAH BLESS YOUR ROLL!"
            ],
            "opponent_bust": [
                "NO WORRIES, {opponent}! STAY POSITIVE!",
                "EVERYTHING IRIE, {opponent}!",
                "BLESS UP! NEXT TIME BETTER!",
                "ONE LOVE, {opponent}!"
            ],
            "game_start": [
                "ONE LOVE, EVERYONE! LET'S PLAY!",
                "JAH BLESS THIS GAME!",
                "POSITIVE VIBES ONLY!",
                "IRIE GAME COMING UP!"
            ],
            "turn_start": [
                "MY TURN! BLESS UP!",
                "JAH GUIDE MY TURN!",
                "IRIE TURN TIME!",
                "ONE LOVE! LET'S GO!"
            ]
        }


class PiratePersonality(BotPersonality):
    """Personality #11: Pirate - Seafaring talk, adventurous, treasure-focused"""
    
    def __init__(self):
        super().__init__("Pirate", ["seafaring", "adventurous", "treasure"])
    
    def _init_message_pools(self) -> Dict[str, List[str]]:
        return {
            "good_roll": [
                "ARRR! THAT BE A FINE ROLL!",
                "SHIVER ME TIMBERS! GOOD DICE!",
                "AVAST! TREASURE IN THEM DICE!",
                "YO HO HO! THAT'S WHAT I'M TALKING ABOUT!"
            ],
            "bad_roll": [
                "BLIMEY! BARNACLES ON THEM DICE!",
                "ARRR, THE SEA BE ROUGH TODAY!",
                "SCURVY DICE! WALK THE PLANK!",
                "SINK ME! THAT BE TERRIBLE!"
            ],
            "bust": [
                "DAVY JONES' LOCKER FOR ME TURN!",
                "ARRR! SHIPWRECKED!",
                "SCUTTLED ME OWN SHIP!",
                "BLOWN TO SMITHEREENS!"
            ],
            "win": [
                "ARRR! I FOUND THE TREASURE!",
                "THE BOOTY BE MINE!",
                "X MARKS THE VICTORY!",
                "CLAIM THE PLUNDER!"
            ],
            "lose": [
                "YE SCURVY DOG! YE WON!",
                "THE BETTER PIRATE WON THIS DAY!",
                "ARRR, BESTED BY A WORTHY FOE!",
                "NEXT TIME, THE TREASURE BE MINE!"
            ],
            "stash_decision": [
                "STASHING ME TREASURE!",
                "HIDING THE BOOTY!",
                "INTO THE CHEST WITH THESE!",
                "SECURING ME PLUNDER!"
            ],
            "bank_decision": [
                "BANKING {points} PIECES OF EIGHT!",
                "TO THE TREASURE HOLD!",
                "ARRR! {points} DOUBLOONS!",
                "SECURE THE GOLD!"
            ],
            "roll_decision": [
                "ROLL THE BONES!",
                "LET'S SEE WHAT THE SEA BRINGS!",
                "CAST THE DICE, MATEY!",
                "ANOTHER ROLL ON THE HIGH SEAS!"
            ],
            "opponent_good_roll": [
                "WELL PLAYED, {opponent}! YE BE A WORTHY SAILOR!",
                "ARRR! GOOD ROLL, MATEY!",
                "FINE ROLLING, {opponent}!",
                "YE FOUND SOME TREASURE THERE!"
            ],
            "opponent_bust": [
                "TOUGH LUCK, {opponent}! THE SEA BE CRUEL!",
                "ARRR, BETTER LUCK NEXT VOYAGE!",
                "{opponent}, YE'LL BOUNCE BACK!",
                "SHAKE IT OFF, SAILOR!"
            ],
            "game_start": [
                "HOIST THE COLORS! LET'S SAIL!",
                "ALL ABOARD! ADVENTURE AWAITS!",
                "SET SAIL FOR VICTORY!",
                "YO HO HO! LET THE GAME BEGIN!"
            ],
            "turn_start": [
                "ME TURN! PREPARE FOR BOARDING!",
                "ARRR! TIME TO CLAIM ME TREASURE!",
                "CAST OFF! ME TURN BEGINS!",
                "FULL SPEED AHEAD!"
            ]
        }


class CynicPersonality(BotPersonality):
    """Personality #12: Cynic - Pessimistic, doubtful, realistic"""
    
    def __init__(self):
        super().__init__("Cynic", ["pessimistic", "doubtful", "realistic"])
    
    def _init_message_pools(self) -> Dict[str, List[str]]:
        return {
            "good_roll": [
                "WELL THAT WON'T LAST.",
                "ENJOY IT WHILE IT LASTS.",
                "PROBABLY THE LAST GOOD ROLL I'LL GET.",
                "SURE, BUT WHAT'S THE CATCH?"
            ],
            "bad_roll": [
                "FIGURES. OF COURSE.",
                "KNEW THAT WAS COMING.",
                "TYPICAL. ABSOLUTELY TYPICAL.",
                "WHY AM I NOT SURPRISED?"
            ],
            "bust": [
                "CALLED IT. SAW THAT COMING.",
                "OF COURSE I BUSTED. NATURALLY.",
                "THIS IS MY LIFE NOW.",
                "EXPECTED NOTHING LESS."
            ],
            "win": [
                "I WON? SOMETHING'S WRONG HERE.",
                "MUST BE A GLITCH.",
                "THIS WON'T HAPPEN AGAIN.",
                "ENJOY IT NOW BEFORE REALITY HITS."
            ],
            "lose": [
                "OBVIOUSLY. AS EXPECTED.",
                "THE UNIVERSE RESTORED BALANCE.",
                "BACK TO NORMAL.",
                "REALITY WINS AGAIN."
            ],
            "stash_decision": [
                "STASHING BEFORE THEY VANISH.",
                "MIGHT AS WELL TRY.",
                "THIS PROBABLY WON'T HELP.",
                "STASHING WITH LOW EXPECTATIONS."
            ],
            "bank_decision": [
                "BANKING {points} BEFORE I LOSE THEM.",
                "SECURING WHAT LITTLE I HAVE.",
                "AT LEAST I GET SOMETHING.",
                "BETTER THAN NOTHING, I GUESS."
            ],
            "roll_decision": [
                "ROLLING. EXPECTING DISAPPOINTMENT.",
                "HERE GOES NOTHING.",
                "LET'S SEE HOW THIS BACKFIRES.",
                "ROLLING AGAINST MY BETTER JUDGMENT."
            ],
            "opponent_good_roll": [
                "OF COURSE YOU GOT THAT.",
                "FIGURES. YOU ALWAYS DO.",
                "YEAH, GREAT FOR YOU.",
                "MUST BE NICE."
            ],
            "opponent_bust": [
                "FINALLY, SOME JUSTICE.",
                "SEE? NOBODY'S SPECIAL.",
                "REALITY CATCHES UP TO EVERYONE.",
                "THAT'S MORE LIKE IT."
            ],
            "game_start": [
                "HERE WE GO AGAIN.",
                "LET'S GET THIS OVER WITH.",
                "ANOTHER GAME, ANOTHER DISAPPOINTMENT.",
                "MIGHT AS WELL START."
            ],
            "turn_start": [
                "MY TURN TO FAIL, I SUPPOSE.",
                "TIME TO BE DISAPPOINTED AGAIN.",
                "HERE COMES NOTHING.",
                "LET'S SEE WHAT GOES WRONG."
            ]
        }


# =============================================================================
# PERSONALITY ASSIGNMENT SYSTEM
# =============================================================================

# Map bot difficulty + number to personality
PERSONALITY_MAP = {
    # EASY BOTS
    "EASY-GO-BOT-1": SportsmanshipPersonality,
    "EASY-GO-BOT-2": OverlyEnthusiasticPersonality,
    "EASY-GO-BOT-3": DullardPersonality,
    "EASY-GO-BOT-4": DadJokePersonality,
    
    # NORMAL BOTS
    "NORMAL-GO-BOT-1": SarcasticPersonality,
    "NORMAL-GO-BOT-2": StonePersonality,
    "NORMAL-GO-BOT-3": PoetPersonality,
    "NORMAL-GO-BOT-4": RastaPersonality,
    
    # HARD BOTS
    "HARD-GO-BOT-1": BraggartPersonality,
    "HARD-GO-BOT-2": HotheadPersonality,
    "HARD-GO-BOT-3": PiratePersonality,
    "HARD-GO-BOT-4": CynicPersonality
}


def get_personality_for_bot(bot_name: str) -> Optional[BotPersonality]:
    """
    Get the personality instance for a bot.
    
    Args:
        bot_name: Bot username (e.g., "EASY-GO-BOT-1", "@NORMAL-GO-BOT-2")
    
    Returns:
        BotPersonality instance or None if not found
    """
    # Remove @ if present
    clean_name = bot_name.replace("@", "")
    
    # Get personality class from map
    personality_class = PERSONALITY_MAP.get(clean_name)
    
    if personality_class:
        return personality_class()
    
    # Default to Sportsmanship if not found
    print(f"Warning: No personality found for {bot_name}, using Sportsmanship")
    return SportsmanshipPersonality()
