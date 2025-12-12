from .morghi_morgh import Morgh
from .morghi_khoros import Khoros
from .morghi_robah import Robah
from .morghi_mar import Mar
from .morghi_loune import Loune
from .morghi_tale import Tale

# NUM CONSTANTS
NUM_OF_PLAYERS: int = 4
MAX_NUM_OF_CARDS_IN_HAND: int = 4
MIN_NUM_OF_CARDS_IN_HAND: int = 4
NUM_OF_MORGHS: int = 11
NUM_OF_KHOROSES: int = 11
NUM_OF_ROBAHS: int = 7
NUM_OF_MARS: int = 4
NUM_OF_TALES: int = 6
NUM_OF_LOUNES: int = 11
NUM_OF_TOKHMS: int = 60

# AVAILABLE CARDS IN THE GAME
AVAILABLE_CARDS=[Morgh, Khoros, Robah, Mar, Loune, Tale]
AVAILABLE_NUM_CARDS=[NUM_OF_MORGHS, NUM_OF_KHOROSES, NUM_OF_ROBAHS, NUM_OF_MARS, NUM_OF_LOUNES, NUM_OF_TALES]
TOTAL_NUM_CARDS=sum(AVAILABLE_NUM_CARDS)

# Rules 
CARDS_FOR_TOKHM_BEZAR = {"Morgh": 1, "Khoros": 1, "Loune": 1}
CARDS_FOR_JOJOO_BEZAR = {"Morgh": 2}