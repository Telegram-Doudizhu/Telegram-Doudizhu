import config
from fun.bot import start_bot

import logging
logging.basicConfig(level = logging.INFO, format = '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s')
logger = logging.getLogger(__name__)

'''
    Global entrance
'''
if __name__ == '__main__':
    logger.warning('TGDDZ preparing to start')

    # TODO: argparse

    start_bot(config.TOKEN, config.PROXY)
