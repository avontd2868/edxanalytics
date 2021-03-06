'''
    Generates a dummy event for testing video analytics
    case 1: getting real data
        python send_event.py localhost:8020 /httpevent
    case 2: getting dummy data
        python send_event.py 2000
'''
import json
import sys
import logging
from logging.handlers import HTTPHandler
# from django.conf import settings
# from logging.handlers import HTTPHandler


def main(argv):
    '''
        Send dummy data over the event handler.
        The event handler inside the module will grab this data.
    '''
    logger = logging.getLogger('video_analytics')
    # http_handler = HTTPHandler('', '', method='GET')
    http_handler = HTTPHandler('127.0.0.1:9999', '/httpevent', method='GET')
    # http_handler = logging.handlers.HTTPHandler('127.0.0.1:9022', '/event', method='GET')

    logger.addHandler(http_handler)
    #logger.setLevel(logging.DEBUG)

    from dummy_values import generate_random_data
    results = generate_random_data(int(argv[1]))
    # logger.critical(json.dumps(["hello", "hi"]))
    # test = ["actor=bob", "action=submitanswer", "object=problem5"]
    # print test  
    # objects = [o.split("=") for o in test]
    # print objects
    # print dict(objects)
    # logger.error(json.dumps(dict(objects)))
    for entry in results:
        # print entry
        # print dict(entry)
        logger.critical(json.dumps(entry))
    # objects = [o.split("=") for o in sys.argv[3:]]
    # logger.error(json.dumps(dict(objects)))

if __name__ == '__main__':
    main(sys.argv)
