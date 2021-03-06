'''
    Store video interactions in the database, query them from the database,
    and visualize video analytics with the queried data.
'''
import sys
import time
import json
from bson import json_util
from collections import defaultdict
from django.conf import settings
# from prototypemodules.common import query_results
from edinsights.core.decorators import view, query, event_handler
# memoize_query
from edxmodules.video_analytics.watching_segments import process_segments, process_heatmaps


@view(name="video_single")
def video_single_view(mongodb, vid):
    ''' Visualize students' interaction with video content
        for a single video segment
    '''
    # bin_size = 5
    # duration = 171
    data = video_single_query(mongodb, vid)
    # video_id = u'2deIoNhqDsg'
    # data = process_data(log_entries)
    #bins = run_counting(segments, bin_size, duration)
    from djanalytics.core.render import render
    return render("heatmap.html", {
        'video_id': vid, 'data': data
    })


# @view(name="video_lecture")
# def video_lecture_view(mongodb):  # def video_heatmap(view)
#     ''' Visualize students' interaction with video content
#         for all videos in a lecture
#     '''
#     # bin_size = 5
#     # duration = 171
#     video_id = "2deIoNhqDsg"
#     log_entries = video_interaction_query()
#     data = process_data(log_entries)
#     #bins = run_counting(segments, bin_size, duration)
#     from djanalytics.core.render import render
#     return render("heatmap.html", {
#         'video_id': video_id, 'data': json.dumps(data)
#     })


# @view(name="video_course")
# def video_course_view(mongodb):  # def video_heatmap(view)
#     ''' Visualize students' interaction with video content
#         over the entire course.
#     '''
#     # bin_size = 5
#     # duration = 171
#     video_id = "2deIoNhqDsg"
#     log_entries = video_interaction_query()
#     data = process_data(log_entries)
#     #bins = run_counting(segments, bin_size, duration)
#     from djanalytics.core.render import render
#     return render("heatmap.html", {
#         'video_id': video_id, 'data': json.dumps(data)
#     })        


@query(name="video_single")
def video_single_query(mongodb, vid):
    ''' Return data from the database. For now returning dummy data. '''
    start_time = time.time()

    collection = mongodb['video_heatmaps']
    entries = list(collection.find({"video_id": vid}))

    if len(entries):
        result = json.dumps(entries[0], default=json_util.default)
    else:
        result = ""
    print sys._getframe().f_code.co_name, "COMPLETED", (time.time() - start_time), "seconds"
    return result


def record_segments(mongodb):
    '''
        construct watching segments from tracking log entries.
    '''
    start_time = time.time()

    collection = mongodb['video_events']
    # For incremental updates, should retrieve only the events that have not been processed yet.
    entries = collection.find({"processed": 0})
    print entries.count(), "new events found"
    data = process_segments(list(entries))
    collection_seg = mongodb['video_segments']
    # collection.remove()
    results = {}
    for video_id in data:
        results[video_id] = {}
        for username in data[video_id]:
            # TOOD: in order to implement incremental updates,
            # we need to combine existing segment data with incoming ones.
            # Probably it's not worth it. Segments are highly unlikely to be cut in the middle.
            # remove all existing (video, username) entries
            # collection2.remove({"video_id": video_id, "user_id": username})
            for segment in data[video_id][username]["segments"]:
                # print data[video_id][username][segment]
                # result = {}
                result = segment
                result["video_id"] = video_id
                result["user_id"] = username
                # print result
                collection_seg.insert(result)
                results[video_id][username] = segment
                # results.append(result)
    # Mark all as processed
    entries.rewind()
    for entry in entries:
        # print "HELLO", entry, entry.keys(), entry["_id"]
        collection.update({"_id": entry["_id"]}, {"processed": 1})
    # Make sure the collection is indexed.
    from pymongo import ASCENDING, DESCENDING
    collection_seg.ensure_index(
        [("video_id", ASCENDING), ("user_id", ASCENDING)])

    print sys._getframe().f_code.co_name, "COMPLETED", (time.time() - start_time), "seconds"
    print results
    return results


def record_heatmaps(mongodb):
    '''
        record heatmap bins for each video, based on segments
        for a single video?
    '''
    start_time = time.time()

    # TODO: handle cut segments (i.e., start event exists but end event missing)
    # TODO: only remove the corresponding entries in the database: (video, user)
    collection = mongodb['video_segments']
    segments = list(collection.find())
    collection = mongodb['video_heatmaps']
    collection.remove()
    print len(segments), "segments found"

    # TODO: store the list of videos that the system currently knows about.
    duration = 171
    results = defaultdict(dict)
    for segment in segments:
        # print results[segment["video_id"]]
        if not segment["user_id"] in results[segment["video_id"]]:
            results[segment["video_id"]][segment["user_id"]] = []
        results[segment["video_id"]][segment["user_id"]].append(segment)
    # print "PRINT", results
    for video_id in results:
        process_heatmaps(mongodb, results[video_id], video_id, duration)

        # process_heatmaps(mongodb, segments[video_id], video_id, duration)
    # for segment in segments:
    #     # print segment
    #     process_heatmaps(mongodb, segment)
    # Make sure the collection is indexed.
    from pymongo import ASCENDING, DESCENDING
    collection.ensure_index([("video_id", ASCENDING)])
        # [("video_id", ASCENDING), ("time", ASCENDING)])

    print sys._getframe().f_code.co_name, "COMPLETED", (time.time() - start_time), "seconds"


# def print_stats(mongodb, vid):
#     start_time = time.time()

#     collection = mongodb['video_heatmaps']
#     entries = list(collection.find({"video_id": vid}))

#     # bins = {}
#     # unique_bins = {}
#     # duration = 171
#     # for index in range(0, duration):
#     #     # print index, len(list(collection.find({"video_id": vid, "time": index})))
#     #     # bins[index] = len(list(collection.find({"video_id": vid, "time": index})))
#     #     res = collection.find_one({"video_id": vid, "time": index})
#     #     # print res, res.keys(), list(res)
#     #     # print len(res), len(list(res)), res["count"]
#     #     if res:
#     #         bins[index] = len(res["count"])
#     #         # for i in res["count"]:
#     #         #     unique_bins[index] = len(res["count"])
#     #     else:
#     #         bins[index] = 0
#     print sys._getframe().f_code.co_name, "COMPLETED", (time.time() - start_time), "seconds"
#     return json.dumps(entries, default=json_util.default)




'''
Tracking Data Source Definition
- make the analytics compatible with multiple data sources

TrackingDataSource
name: name of the source (e.g., "EDX_VIDEO")
event_types: list of event types to track (e.g., ["play_video", "pause_video"])
'''

@event_handler()
def video_interaction_event(mongodb, events):
    ''' Store all video-related events from the tracking log
        into the database. There are three collections:
        1) video_events: raw event information
        2) video_segments: watching segments recovered from events
        3) video_heatmap: view counts for each second of a video
    '''
    print "=========== HERE ============="
    # Store raw event information
    for event in events:
        entry = {}
        for key in event.keys():
            entry[key] = event[key]
            # flag indicating whether this item has been processed for segments and heatmaps
            entry["processed"] = 0
        collection = mongodb['video_events']
        if event["event_type"] in ("play_video", "pause_video"):
            # print entry
            collection.insert(entry)


# @query(name="show_stats")
# def show_stats(mongodb, vid):
#     start_time = time.time()
#     bins = print_stats(mongodb, vid) 
#     print sys._getframe().f_code.co_name, "COMPLETED", (time.time() - start_time), "seconds"
#     return bins


@query(name="process_data")
def process_data(mongodb):
    start_time = time.time()

    segments = record_segments(mongodb)
    record_heatmaps(mongodb)
    print sys._getframe().f_code.co_name, "COMPLETED", (time.time() - start_time), "seconds"
    return "DONE"

