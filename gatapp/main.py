import threading
from datetime import datetime
from time import sleep
from bokeh.models import (
    ColumnDataSource,
    WMTSTileSource,
    Range1d,
    HoverTool,
    PanTool,
    WheelZoomTool,
    BoxZoomTool,
    ResetTool
)
from bokeh.plotting import (
    figure,
    curdoc
)
from bokeh.layouts import row
from gat_config import route, make_test_route, get_nysf_route
import gat_stream

#route = make_test_route()
#route = get_nysf_route()

print(route)

class Listeners(threading.Thread):

    def __init__(self):
        self.listeners = {r['start']: gat_stream.Listener(r['stop'], r['box']) for r in route}
        self.first_started = False
        self.started_listeners = []
        self.killed_listeners = []
        self._stop_event = threading.Event()
        threading.Thread.__init__(self)

    def get(self):
        time = datetime.strftime(datetime.utcnow(), '%Y%m%d %H%M')
        return self.listeners.get(time)

    def stop(self):
        gat_stream.data_handler.save_data()
        self._stop_event.set()

    def show_count(self):
        print(
            'started: {}, stopped: {}'.format(
                len(self.started_listeners),
                len(self.killed_listeners)
            )
        )

    def run(self):
        while True:
            if self._stop_event.is_set():
                break
            listener = self.get()
            if listener:
                try:
                    listener.start()
                    self.started_listeners.append(listener)
                    if len(self.started_listeners) == 1:
                        print('started first listener')
                        self.first_started = True
                    else:
                        print('started new listener')
                    self.show_count()
                except RuntimeError: #thread already started
                    pass
            if self.first_started:
                for l in self.started_listeners:
                    if l.stopped() and l not in self.killed_listeners:
                        self.killed_listeners.append(l)
                        self.show_count()
                if len(self.started_listeners) == len(self.killed_listeners):
                    self.stop()
            sleep(0.5)

    def stopped(self):
        return self._stop_event.is_set()


# start the Listeners
gat_listeners = Listeners()
gat_listeners.start()

def kill_threads():
    gat_listeners.stop()
    for l in gat_listeners.started_listeners:
        if not l.stopped():
            l.stop()
        l.join()
    gat_listeners.join()
    gat_stream.stop_clock()
    print('done...with {} threads still active'.format(threading.active_count()))    

data = ColumnDataSource({col: [] for col in gat_stream.data_handler.columns})
tile_options = {
    'url': 'https://cartodb-basemaps-b.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png'
}
tile_source = WMTSTileSource(**tile_options)
x_range = Range1d(start=-14000000, end=-8000000, bounds=None)
y_range = Range1d(start=1800000, end=5800000, bounds=None)

hover = HoverTool(tooltips="""
<div style="max-width: 300px;">
  <a href="@url" target="_blank">
    <img style="max-height: 100%; max-width: 100%" src="@display_img"></img>
  </a>
</div>
"""
)

gat_plot = figure(
    plot_width=1400,
    plot_height=1000,
    x_range=x_range,
    y_range=y_range,
    tools=[hover, ResetTool(), BoxZoomTool(), WheelZoomTool(), PanTool()],
    title='Great American Tweets'
)
gat_plot.axis.visible = False
gat_plot.add_tile(tile_source)
gat_plot.circle(x='x', y='y', size=7, source=data)


def update_data():
    new_data = gat_stream.data_handler.get_new_data()
    try:
        data.stream(new_data)
    except ValueError:
        pass

curdoc().add_root(row(gat_plot, width=1600))
curdoc().title = "Great American Tweets"
curdoc().add_periodic_callback(update_data, 1000)

def tkill():
    while True:
        if gat_listeners.stopped():
            print('all listeners stopped...killing loose threads')
            kill_threads()
            break

t = threading.Thread(target=tkill)
t.start()

