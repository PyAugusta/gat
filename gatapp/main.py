import threading
from datetime import datetime, timedelta
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
from gat_config import route
import gat_stream


def get_timerange(plus_seconds, start=datetime.now()):
    n = start + timedelta(seconds=5)
    e = n + timedelta(seconds=plus_seconds)
    return n, e

nypoi = [-74,40,-73,41]
_nystart, _nyend = get_timerange(120)
nystart = datetime.strftime(_nystart, '%Y%m%d %H%M')
nyend = datetime.strftime(_nyend, '%Y%m%d %H%M')

sfpoi = [-122.75,36.8,-121.75,37.8]
_sfstart, _sfend = get_timerange(120, start=_nyend)
sfstart = datetime.strftime(_sfstart, '%Y%m%d %H%M')
sfend = datetime.strftime(_sfend, '%Y%m%d %H%M')

test_route = [{'start': nystart, 'stop': nyend, 'box': nypoi},
              {'start': sfstart, 'stop': sfend, 'box': sfpoi}]
print(test_route)

listeners = {r['start']: gat_stream.Listener(r['stop'], r['box']) for r in test_route}
active_listeners = []

class Listeners(threading.Thread):

  def __init__(self):
    self.listeners = {r['start']: gat_stream.Listener(r['stop'], r['box']) for r in test_route}
    self.active_listeners = []
    self._stop_event = threading.Event()
    threading.Thread.__init__(self)

  def get(self):
    time = datetime.strftime(datetime.now(), '%Y%m%d %H%M')
    return listeners.get(time)

  def run(self):
    while True:
        if self._stop_event.is_set():
            break
        listener = self.get()
        if listener:
            try:
                listener.start()
                self.active_listeners.append(listener)
            except RuntimeError: #thread already started
                pass
        sleep(1)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


# start the Listeners
gat_listeners = Listeners()
gat_listeners.start()


data = ColumnDataSource({col: [] for col in gat_stream.data_handler.columns})
tile_options = {
    'url': 'https://cartodb-basemaps-b.global.ssl.fastly.net/dark_all/{z}/{x}/{y}.png'
}
tile_source = WMTSTileSource(**tile_options)
x_range = Range1d(start=-12500000, end=-7700000, bounds=None)
y_range = Range1d(start=3000000, end=5000000, bounds=None)

hover = HoverTool(tooltips="""
<div style="max-width: 300px;">
  <img style="max-height: 100%; max-width: 100%" src="@display_img"></img>
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
