# main.py - Streak Control (Kivy) - Redmi Note 13 Pro preview
import os, json, time, datetime
from collections import Counter
from kivy.config import Config
import sys
if sys.platform != 'android':
    Config.set('graphics', 'width', '393')
    Config.set('graphics', 'height', '852')
    Config.set('graphics', 'resizable', '0')

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line, InstructionGroup
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.metrics import dp, sp

try:
    from android.storage import app_storage_path
    DATA_FILE = os.path.join(app_storage_path(), 'streak_control.json')
except Exception:
    DATA_FILE = os.path.join(os.path.expanduser('~'), '.streak_control.json')

# ---- dark palette ----
BG = (0.05, 0.06, 0.12, 1)
CARD = (0.10, 0.12, 0.20, 1)
CARD2 = (0.13, 0.15, 0.24, 1)
INK = (0.93, 0.94, 0.97, 1)
GRAY = (0.55, 0.58, 0.68, 1)
PURPLE = (0.73, 0.36, 0.98, 1)
TEAL = (0.30, 0.85, 0.75, 1)
RED = (0.95, 0.30, 0.40, 1)

KV = r'''
<RingWidget>:
    BoxLayout:
        orientation: 'vertical'
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        size_hint: 0.62, 0.7
        Label:
            text: 'CURRENT STREAK'
            font_size: sp(11)
            bold: True
            color: 0.62,0.66,0.78,1
            size_hint_y: None
            height: dp(16)
        Label:
            text: root.days_text
            font_size: sp(40)
            bold: True
            color: 1,1,1,1
            size_hint_y: None
            height: dp(48)
        Label:
            text: root.time_text
            font_size: sp(26)
            bold: True
            color: 1,1,1,1
            size_hint_y: None
            height: dp(34)
        Label:
            text: root.secs_text
            font_size: sp(18)
            bold: True
            color: 0.30,0.85,0.75,1
            size_hint_y: None
            height: dp(24)
        Label:
            text: 'OF SOBRIETY'
            font_size: sp(10)
            bold: True
            color: 0.62,0.66,0.78,1
            size_hint_y: None
            height: dp(16)

<StreakRoot>:
    orientation: 'vertical'
    padding: dp(16)
    spacing: dp(12)
    canvas.before:
        Color:
            rgba: 0.05,0.06,0.12,1
        Rectangle:
            pos: self.pos
            size: self.size

    # Header
    BoxLayout:
        size_hint_y: None
        height: dp(40)
        Label:
            text: 'Streak Control'
            font_size: sp(18)
            bold: True
            color: 0.93,0.94,0.97,1
            halign: 'left'
            valign: 'middle'
            text_size: self.size
        Button:
            text: '≡'
            size_hint_x: None
            width: dp(40)
            background_normal: ''
            background_color: 0.10,0.12,0.20,1
            color: 1,1,1,1
            font_size: sp(22)
            on_press: root.open_history()

    # Ring timer
    BoxLayout:
        size_hint_y: None
        height: dp(240)
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0.10,0.12,0.20,1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(24)]
        RingWidget:
            id: ring
            days_text: root.days_text
            time_text: root.time_text
            secs_text: root.secs_text

    # Remaining line
    Label:
        id: remain_lbl
        text: root.remain_text
        font_size: sp(13)
        bold: True
        color: 0.93,0.94,0.97,1
        size_hint_y: None
        height: dp(20)

    # Target + Best
    BoxLayout:
        size_hint_y: None
        height: dp(56)
        spacing: dp(10)
        StatCard:
            title: 'TARGET TO BEAT'
            value: root.target_text
            accent: 0.30,0.85,0.75,1
        StatCard:
            title: 'BEST STREAK'
            value: root.best_text
            accent: 0.73,0.36,0.98,1

    # Relapse button
    Button:
        text: 'I RELAPSED'
        size_hint_y: None
        height: dp(54)
        background_normal: ''
        background_color: 0.95,0.30,0.40,1
        color: 1,1,1,1
        bold: True
        font_size: sp(15)
        on_press: root.do_relapse()

    # Action row
    BoxLayout:
        size_hint_y: None
        height: dp(42)
        spacing: dp(10)
        Button:
            text: 'History'
            background_normal: ''
            background_color: 0.10,0.12,0.20,1
            color: 1,1,1,1
            font_size: sp(13)
            on_press: root.open_history()
        Button:
            text: 'Keep awake: ' + ('ON' if root.keep_awake else 'OFF')
            background_normal: ''
            background_color: (0.30,0.85,0.75,1) if root.keep_awake else (0.10,0.12,0.20,1)
            color: 1,1,1,1
            font_size: sp(13)
            on_press: root.toggle_keep()

    # Stats grid
    GridLayout:
        cols: 4
        size_hint_y: None
        height: dp(72)
        spacing: dp(8)
        MiniStat:
            label: 'Relapses'
            value: root.stat_relapses
        MiniStat:
            label: 'Today'
            value: root.stat_today
        MiniStat:
            label: 'Max/day'
            value: root.stat_maxday
        MiniStat:
            label: 'Avg gap'
            value: root.stat_avg

    Label:
        id: last_lbl
        text: 'Last: --'
        font_size: sp(11)
        color: 0.55,0.58,0.68,1
        size_hint_y: None
        height: dp(16)
        halign: 'center'
        text_size: self.size

<StatCard@BoxLayout>:
    orientation: 'vertical'
    padding: dp(12)
    canvas.before:
        Color:
            rgba: 0.10,0.12,0.20,1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16)]
    title: ''
    value: ''
    accent: 1,1,1,1
    Label:
        text: root.title
        font_size: sp(9)
        color: 0.62,0.66,0.78,1
        size_hint_y: None
        height: dp(14)
    Label:
        text: root.value
        font_size: sp(16)
        bold: True
        color: root.accent
        size_hint_y: None
        height: dp(24)

<MiniStat@BoxLayout>:
    orientation: 'vertical'
    padding: dp(6)
    canvas.before:
        Color:
            rgba: 0.10,0.12,0.20,1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]
    label: ''
    value: ''
    Label:
        text: root.value
        font_size: sp(18)
        bold: True
        color: 1,1,1,1
        size_hint_y: None
        height: dp(26)
    Label:
        text: root.label
        font_size: sp(9)
        color: 0.55,0.58,0.68,1
        size_hint_y: None
        height: dp(12)

<HistoryPopup>:
    orientation: 'vertical'
    padding: dp(12)
    spacing: dp(8)
    canvas.before:
        Color:
            rgba: 0.05,0.06,0.12,1
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: 'History'
        font_size: sp(18)
        bold: True
        color: 1,1,1,1
        size_hint_y: None
        height: dp(30)
    ScrollView:
        Accordion:
            id: acc
            orientation: 'vertical'
    BoxLayout:
        size_hint_y: None
        height: dp(44)
        Button:
            text: 'Close'
            background_normal: ''
            background_color: 0.10,0.12,0.20,1
            color: 1,1,1,1
            on_press: root.dismiss_popup()
'''

QUOTES = [
    "Life can be drastically different in just a matter of WEEKS.",
    "Discipline is choosing between what you want now and what you want most.",
    "Every streak broken is a lesson, not a failure.",
    "You are stronger than your urges.",
    "The pain of discipline is less than the pain of regret.",
    "Your future self is watching. Make them proud.",
    "Mastery is not about never falling, but always rising.",
    "Control the urge, or the urge controls you.",
]


class RingWidget(FloatLayout):
    days_text = StringProperty('0')
    time_text = StringProperty('0 Hrs 0 Mins')
    secs_text = StringProperty('0 secs')

    def __init__(self, **kw):
        super().__init__(**kw)
        self._pct = 0.0
        self._grp = InstructionGroup()
        self.canvas.add(self._grp)
        self.bind(pos=self._redraw, size=self._redraw)
        Clock.schedule_once(lambda *_: self._redraw(), 0)

    def set_progress(self, pct):
        self._pct = max(0.0, min(100.0, float(pct)))
        self._redraw()

    def _redraw(self, *a):
        if self.width <= 0 or self.height <= 0:
            return
        x, y = self.pos
        w, h = self.size
        d = min(w, h) - 20
        ex, ey = x + (w - d) / 2.0, y + (h - d) / 2.0
        g = self._grp
        g.clear()
        g.add(Color(0.20, 0.22, 0.32, 1))
        g.add(Line(ellipse=(ex, ey, d, d), width=12))
        sweep = 360.0 * self._pct / 100.0
        if sweep <= 0:
            return
        start = 90.0
        if sweep <= 180:
            g.add(Color(*PURPLE))
            g.add(Line(ellipse=(ex, ey, d, d, start - sweep, start), width=12))
        else:
            g.add(Color(*PURPLE))
            g.add(Line(ellipse=(ex, ey, d, d, start - 180, start), width=12))
            g.add(Color(*RED))
            g.add(Line(ellipse=(ex, ey, d, d, start - sweep, start - 180), width=12))


class StreakRoot(BoxLayout):
    days_text = StringProperty('0')
    time_text = StringProperty('0 Hrs 0 Mins')
    secs_text = StringProperty('0 secs')
    remain_text = StringProperty('Set your first streak to create a target.')
    target_text = StringProperty('No best yet')
    best_text = StringProperty('0d')
    stat_relapses = StringProperty('0')
    stat_today = StringProperty('0')
    stat_maxday = StringProperty('0')
    stat_avg = StringProperty('--')
    keep_awake = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.last_relapse = None
        self.history = []
        self.best_ms = 0
        self.last_reset_year = None
        self.load()
        self.check_new_year()
        if self.last_relapse is None:
            self.last_relapse = time.time()
            self.save()
        Clock.schedule_interval(self.tick, 1.0)
        Clock.schedule_once(lambda *_: self.tick(0), 0)

    # ---------- persistence ----------
    def load(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE) as f:
                    d = json.load(f)
                self.last_relapse = d.get('last_relapse')
                self.history = d.get('history', [])
                self.best_ms = d.get('best_ms', 0)
                self.keep_awake = d.get('keep_awake', False)
                self.last_reset_year = d.get('last_reset_year', None)
        except Exception as e:
            print('load err', e)

    def save(self):
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump({
                    'last_relapse': self.last_relapse,
                    'history': self.history,
                    'best_ms': self.best_ms,
                    'keep_awake': self.keep_awake,
                    'last_reset_year': self.last_reset_year,
                }, f)
        except Exception as e:
            print('save err', e)

    def check_new_year(self):
        y = datetime.datetime.now().year
        if self.last_reset_year is None:
            self.last_reset_year = y
            self.save()
            return
        if y != self.last_reset_year:
            self.last_relapse = time.time()
            self.history = []
            self.best_ms = 0
            self.last_reset_year = y
            self.save()

    # ---------- formatting ----------
    @staticmethod
    def fmt_ms(ms):
        if ms < 0:
            ms = 0
        s = int(ms // 1000)
        d = s // 86400
        h = (s % 86400) // 3600
        m = (s % 3600) // 60
        sec = s % 60
        if d > 0:
            return f'{d}d {h:02d}:{m:02d}:{sec:02d}'
        return f'{h:02d}:{m:02d}:{sec:02d}'

    @staticmethod
    def fmt_short(ms):
        if ms < 0:
            ms = 0
        s = int(ms // 1000)
        d = s // 86400
        h = (s % 86400) // 3600
        m = (s % 3600) // 60
        if d > 0:
            return f'{d}d {h}h'
        if h > 0:
            return f'{h}h {m}m'
        return f'{m}m'

    @staticmethod
    def fmt_date(ts):
        return datetime.datetime.fromtimestamp(ts).strftime('%b %d, %H:%M')

    # ---------- tick ----------
    def tick(self, dt):
        self.check_new_year()
        now = time.time()
        elapsed_ms = (now - self.last_relapse) * 1000.0
        s = int(elapsed_ms // 1000)
        days = s // 86400
        hrs = (s % 86400) // 3600
        mins = (s % 3600) // 60
        secs = s % 60
        self.days_text = str(days)
        self.time_text = f'{hrs} Hrs  {mins} Mins'
        self.secs_text = f'{secs} secs'

        best = self.best_ms
        self.target_text = self.fmt_ms(best) if best > 0 else 'No best yet'
        self.best_text = self.fmt_short(best) if best > 0 else '0d'
        if best > 0:
            self.ids.ring.set_progress(min(100.0, elapsed_ms / best * 100.0))
            if elapsed_ms >= best:
                self.remain_text = 'NEW RECORD! You beat your best.'
            else:
                self.remain_text = f'{self.fmt_ms(best - elapsed_ms)} left to beat your best.'
        else:
            self.ids.ring.set_progress(0)
            self.remain_text = 'Your first streak sets the target.'

        self.stat_relapses = str(len(self.history))
        today = datetime.date.today()
        today_cnt = sum(1 for ts in self.history if datetime.datetime.fromtimestamp(ts).date() == today)
        day_counts = Counter(datetime.datetime.fromtimestamp(ts).date() for ts in self.history)
        self.stat_today = str(today_cnt)
        self.stat_maxday = str(max(day_counts.values())) if day_counts else '0'
        if len(self.history) >= 2:
            sh = sorted(self.history)
            gaps = [sh[i + 1] - sh[i] for i in range(len(sh) - 1)]
            self.stat_avg = self.fmt_short(sum(gaps) / len(gaps) * 1000.0)
        else:
            self.stat_avg = '--'

        self.ids.last_lbl.text = 'Last relapse: ' + self.fmt_date(self.last_relapse)

    # ---------- actions ----------
    def do_relapse(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text='Log a relapse now?\nThis resets your current streak.',
                                 halign='center', color=INK))
        popup = Popup(title='Confirm', content=content, size_hint=(0.85, 0.35))

        def yes(*_):
            now = time.time()
            streak = (now - self.last_relapse) * 1000.0
            if streak > self.best_ms:
                self.best_ms = streak
            self.history.insert(0, now)
            if len(self.history) > 500:
                self.history = self.history[:500]
            self.last_relapse = now
            self.save()
            popup.dismiss()
            self.tick(0)

        def no(*_):
            popup.dismiss()

        btns = BoxLayout(size_hint_y=None, height=44, spacing=10)
        btns.add_widget(Button(text='Yes', background_color=RED, on_press=yes))
        btns.add_widget(Button(text='Cancel', background_color=(0.10, 0.12, 0.20, 1), on_press=no))
        content.add_widget(btns)
        popup.open()

    def open_history(self):
        content = HistoryPopup(streak=self)
        content.refresh()
        self._hist_popup = Popup(title='', content=content, size_hint=(0.92, 0.88),
                                 separator_height=0, background_color=(0, 0, 0, 0))
        self._hist_popup.open()

    def toggle_keep(self):
        self.keep_awake = not self.keep_awake
        self.save()
        try:
            from plyer import keepawake
            if self.keep_awake:
                keepawake.keep_screen_on()
            else:
                keepawake.allow_screen_sleep()
        except Exception:
            pass


class HistoryPopup(BoxLayout):
    def __init__(self, streak, **kwargs):
        super().__init__(**kwargs)
        self.streak = streak

    def refresh(self):
        acc = self.ids.acc
        acc.clear_widgets()
        if not self.streak.history:
            item = AccordionItem(title='No history yet')
            item.add_widget(Label(text='Stay strong. No relapses logged.', color=GRAY))
            acc.add_widget(item)
            return
        groups = {}
        for ts in self.streak.history:
            d = datetime.datetime.fromtimestamp(ts).date()
            groups.setdefault(d, []).append(ts)
        for d in sorted(groups.keys(), reverse=True):
            entries = groups[d]
            item = AccordionItem(title='%s  (%d)' % (d.strftime('%b %d, %Y'), len(entries)))
            box = BoxLayout(orientation='vertical', spacing=4, padding=6, size_hint_y=None)
            box.bind(minimum_height=box.setter('height'))
            for i, ts in enumerate(entries):
                row = BoxLayout(size_hint_y=None, height=34, padding=(8, 0))
                with row.canvas.before:
                    Color(0.10, 0.12, 0.20, 1)
                    RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(8)])
                lbl = Label(text=self.streak.fmt_date(ts), color=INK, halign='left', valign='middle')
                lbl.bind(size=lambda w, s: setattr(w, 'text_size', s))
                lbl.size_hint_x = 0.7
                row.add_widget(lbl)
                row.add_widget(Label(text='#%d' % (i + 1), size_hint_x=None, width=40, color=GRAY))
                box.add_widget(row)
            item.add_widget(box)
            acc.add_widget(item)

    def dismiss_popup(self):
        p = self.parent
        while p is not None and not isinstance(p, Popup):
            p = p.parent
        if p:
            p.dismiss()


Builder.load_string(KV)


class StreakApp(App):
    def build(self):
        Window.clearcolor = BG
        Clock.schedule_once(self._center_window, 0.5)
        return StreakRoot()

    def _center_window(self, *a):
        try:
            sw, sh = Window.system_size
            Window.left = max(0, (sw - Window.width) // 2)
            Window.top = max(0, (sh - Window.height) // 2)
        except Exception as e:
            print('center err', e)


if __name__ == '__main__':
    StreakApp().run()
