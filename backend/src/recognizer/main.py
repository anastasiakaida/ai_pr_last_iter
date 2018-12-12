import traceback
import argparse

from agent import AgentBuilder
from detector import DETECTOR
from matcher import MATCHER
from enviroment import ENVIROMENT
from item import Item
from image import ImagePath

import cv2

parser = argparse.ArgumentParser(description='Main recognizer runner')
parser.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        help='create verbose agent'
        )
parser.add_argument(
        '--not-smart',
        dest='not_smart',
        action='store_true',
        help='create dumb agent, this agent calculates item descriptors \
                and keypoints every time'
        )
parser.add_argument(
        '-d', '--detector',
        dest='detector',
        action='store',
        choices=DETECTOR,
        default=DETECTOR[3],
        help='detector to use in agent'
        )
parser.add_argument(
        '-m', '--matcher',
        dest='matcher',
        action='store',
        choices=MATCHER,
        default=MATCHER[2],
        help='matcher to use in agent',
        )
parser.add_argument(
        '-et', '--enviroment-type',
        dest='enviroment',
        action='store',
        choices=ENVIROMENT,
        default=ENVIROMENT[0],
        help='enviroment in which agent will search for object'
        )
parser.add_argument(
        '-ev', '--enviroment-value',
        dest='evalue',
        action='store',
        default=None,
        help='ID of camera or path to media'
        )
parser.add_argument(
        '-i', '--item',
        dest='item',
        action='store',
        required=True,
        help='path to image of item which agent will search for'
        )
parser.add_argument(
        '--save',
        dest='save',
        type=str,
        default=None,
        help='file name to save recognition result image'
        )

def main(_agent, save):
    if save is None:
        while True:
            _agent.run()
    else:
        while True:
           img, coords, timestamp =  _agent.run()
           cv2.imwrite(save, img)
  
if __name__ == "__main__":
    args = parser.parse_args()

    # Validate enviroment value
    if args.enviroment != ENVIROMENT[0] and args.evalue is None:
        parser.print_usage()
        print('{}: error: the following arguments are required: \
                -ev/--enviroment-value'.format(parser.prog)
            )
        exit(1)
    elif args.evalue is None:
        args.evalue = 0

    try:

        item = Item(args.item.split('/')[-1:][0], ImagePath(args.item))
        ab = AgentBuilder()
        a = ab.get_agent(
                args.debug,
                args.not_smart,
                args.detector,
                args.matcher,
                args.enviroment,
                args.evalue,
                None,
                None,
                item
                )
        main(a, args.save)
        
    except Exception as e:
        print(e)
        traceback.print_tb(e.__traceback__)    
        exit(1)
