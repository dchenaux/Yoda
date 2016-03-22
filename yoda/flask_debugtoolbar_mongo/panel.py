from flask_debugtoolbar.panels import DebugPanel
import jinja2
from . import operation_tracker
from . import jinja_filters



class MongoDebugPanel(DebugPanel):
    """Panel that shows information about MongoDB operations.
    """
    name = 'Mongo'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(MongoDebugPanel, self).__init__(*args, **kwargs)
        self.jinja_env.loader = jinja2.ChoiceLoader([
            self.jinja_env.loader,
            jinja2.PrefixLoader({
                'debug_tb_mongo': jinja2.PackageLoader(__name__, 'templates')
            })
        ])
        filters = ('format_stack_trace', 'embolden_file', 'format_dict',
                   'highlight', 'pluralize')
        for jfilter in filters:
            self.jinja_env.filters[jfilter] = getattr(jinja_filters, jfilter)
        operation_tracker.install_tracker()

    def process_request(self, request):
        operation_tracker.reset()

    def nav_title(self):
        return 'MongoDB'

    def nav_subtitle(self):
        fun = lambda x, y: (x, len(y), '%.2f' % sum(z['time'] for z in y))
        ctx = {'operations': [], 'count': 0, 'time': 0}

        if operation_tracker.queries:
            ctx['operations'].append(fun('read', operation_tracker.queries))
            ctx['count'] += len(operation_tracker.queries)
            ctx['time'] += sum(x['time'] for x in operation_tracker.queries)

        if operation_tracker.inserts:
            ctx['operations'].append(fun('insert', operation_tracker.inserts))
            ctx['count'] += len(operation_tracker.inserts)
            ctx['time'] += sum(x['time'] for x in operation_tracker.inserts)

        if operation_tracker.updates:
            ctx['operations'].append(fun('update', operation_tracker.updates))
            ctx['count'] += len(operation_tracker.updates)
            ctx['time'] += sum(x['time'] for x in operation_tracker.updates)

        if operation_tracker.removes:
            ctx['operations'].append(fun('delete', operation_tracker.removes))
            ctx['count'] += len(operation_tracker.removes)
            ctx['time'] += sum(x['time'] for x in operation_tracker.removes)

        ctx['time'] = '%.2f' % ctx['time']
        return self.render('debug_tb_mongo/mongo-panes-subtitle.html', ctx)

    def title(self):
        return 'MongoDB Operations'

    def url(self):
        return ''

    def content(self):
        context = self.context.copy()
        context['queries'] = operation_tracker.queries
        context['inserts'] = operation_tracker.inserts
        context['updates'] = operation_tracker.updates
        context['removes'] = operation_tracker.removes
        return self.render('debug_tb_mongo/mongo-panel.html', context)
