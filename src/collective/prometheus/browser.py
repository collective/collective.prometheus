import sys
from time import time

from Products.Five.browser import BrowserView
from zExceptions import NotFound
from ZODB.ActivityMonitor import ActivityMonitor
try:
    import ZServer.PubCore
    Z_SERVER = True
except Exception:
    Z_SERVER = False


def metric(name, value, metric_type=None, help_text=None, thread=None):
    HELP_TMPL = '# HELP {0} {1}\n'
    TYPE_TMPL = '# TYPE {0} {1}\n'
    output = ''
    if help_text is not None:
        output += HELP_TMPL.format(name, help_text)
    if metric_type is not None:
        output += TYPE_TMPL.format(name, metric_type)
    if thread:
        name = name + '{thread="' + str(thread) + '"}'
    output += '{0} {1}\n'.format(name, value)
    return output


class Prometheus(BrowserView):

    def __call__(self, *args, **kwargs):
        result = []
        if Z_SERVER:
            result.extend(self.zopethreads())
        result.extend(self.zopecache())
        result.extend(self.zodbactivity())
        result.extend(self.zopeconnections())
        return ''.join(result)

    def _getdbs(self):
        filestorage = self.request.get('filestorage')
        db = self.context.unrestrictedTraverse('/Control_Panel/Database')
        if filestorage == '*':
            db = self.context.unrestrictedTraverse('/Control_Panel/Database')
            for filestorage in db.getDatabaseNames():
                yield (db[filestorage], '_%s' % filestorage)
        elif filestorage:
            if filestorage not in db.getDatabaseNames():
                raise NotFound
            yield (db[filestorage], '')
        else:
            yield (db['main'], '')

    def zopethreads(self):
        if sys.version_info < (2, 5):
            import threadframe
            thread = threadframe.dict
        else:
            thread = sys._current_frames
        frames = thread()
        total_threads = len(frames)
        if ZServer.PubCore._handle is not None:
            handler_lists = ZServer.PubCore._handle.im_self._lists
        else:
            handler_lists = ((), (), ())
        # Check the ZRendevous __init__ for the definitions below
        busy_count, request_queue_count, free_count = [
            len(l) for l in handler_lists
        ]
        return [
            metric(
                'zope_total_threads', total_threads, 'gauge',
                'The number of running Zope threads'
            ),
            metric(
                'zope_free_threads', free_count, 'gauge',
                'The number of Zope threads not in use'
            ),
        ]

    def zopecache(self):
        """ zodb cache statistics """
        result = []
        for (db, suffix) in self._getdbs():
            result.extend(self._zopecache(db, suffix))
        return result

    def _zopecache(self, db, suffix):
        return [
            metric(
                'zope_total_objects' + suffix, db.database_size(), 'gauge',
                'The number of objects in the Zope database',
            ),
            metric(
                'zope_cache_memory' + suffix, db.cache_length(), 'gauge',
                'Memory used by the Zope cache',
            ),
            metric(
                'zope_cache_size' + suffix, db.cache_size(), 'gauge',
                'The number of objects that can be stored in the Zope cache',
            ),
        ]

    def zodbactivity(self):
        """ zodb activity statistics """
        result = []
        for (db, suffix) in self._getdbs():
            result.extend(self._zodbactivity(db, suffix))
        return result

    def _zodbactivity(self, db, suffix):
        now = time()
        start = now - 15  # Prometheus polls every 15 seconds
        end = now
        zodb = db._getDB()
        if zodb.getActivityMonitor() is None:
            zodb.setActivityMonitor(ActivityMonitor())
        data = zodb.getActivityMonitor().getActivityAnalysis(
            start=start, end=end, divisions=1
        )[0]
        return [
            metric(
                'zodb_connections' + suffix, data['connections'],
                'gauge', 'ZODB connections'
            ),
            metric(
                'zodb_load_count' + suffix, data['loads'],
                'gauge', 'ZODB load count'
            ),
            metric(
                'zodb_store_count' + suffix, data['stores'],
                'gauge', 'ZODB store count'
            ),
        ]

    def _zopeconnections(self, db, suffix):
        zodb = db._p_jar.db()
        result = []
        # try to keep the results in a consistent order
        sorted_cache_details = sorted(
            zodb.cacheDetailSize(), key=lambda m: m['connection']
        )
        for (conn_id, conn_data) in enumerate(sorted_cache_details):
            total = conn_data.get('size', 0)
            active = metric(
                'zope_connection_active_objects',
                conn_data.get('ngsize', 0), 'gauge', 'Active Zope Objects',
                thread=conn_id,
            )
            result.append(active)
            total = metric(
                'zope_connection_total_objects',
                conn_data.get('size', 0), 'gauge', 'Total Zope Objects',
                thread=conn_id,
            )
            result.append(total)
        return result

    def zopeconnections(self):
        result = []
        for (db, suffix) in self._getdbs():
            result.extend(self._zopeconnections(db, suffix))
        return result
