"""
SpellChecker.py - Check the spplling of a word using the HunSpellChecker.
"""

from logging import getLogger, debug, error

from hunspell import Hunspell

__author__ = 'Travis Risner'
__project__ = "WordTrekSolver"
__creation_date__ = "{DATE}"
# "${CopyRight.py}"

log = getLogger(__name__)


class HunSpellCheckerClass:
    """
    Check the spelling of a word.
    """

    def __init__(self):
        """
        Set up for the checking the spelling of a word.
        """
        debug('Initializing Hunspell')
        self.word_check = Hunspell()
        # config_list = self.word_check.ConfigKeys()
        # # print(config_list:'encoding')
        # for config_item in config_list:
        #     print('\n', config_item, config_list[config_item])

    def check_word(self, test_word: str) -> bool:
        """
        Check a word to see if it is spelled correctly.

        Note: It appears that a lot of abbreviations are in the aspell
        dictionary, such as 'ac' and 'cf'.  I will just have to manually
        weed them out with the ole Mark One eyeball.  :)

        :param test_word: word to check
        :return: true if spelled ok or false if not a valid word
        """
        debug(f'check_word received {test_word}')
        result = self.word_check.spell(test_word.lower())
        debug(f'check_word result {result}')
        return result

# EOF
