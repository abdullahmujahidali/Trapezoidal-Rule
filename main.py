import random
import tkinter as tk
import math


class DrawingCanvas():
    """ A canvas drawing manager """

    def __init__(self, canvas, wxmin, wymin, wxmax, wymax, dmargin, y_is_flipped):
        self.canvas = canvas
        self.wxmin = wxmin
        self.wymin = wymin
        self.wxmax = wxmax
        self.wymax = wymax
        self.dmargin = dmargin
        self.y_is_flipped = y_is_flipped

        self.set_scales()

    def set_scales(self):
        """ Calculate scale parameters for the canvas's current size. """
        self.canvas.update()
        self.dxmin = self.dmargin
        self.dymin = self.dmargin
        self.dxmax = self.canvas.winfo_width() - self.dmargin - 1
        self.dymax = self.canvas.winfo_height() - self.dmargin - 1

        # Flip the coordinates to invert the result
        if self.y_is_flipped:
            self.dymin, self.dymax = self.dymax, self.dymin

        self.xscale = (self.dxmax - self.dxmin) / (self.wxmax - self.wxmin)
        self.yscale = (self.dymax - self.dymin) / (self.wymax - self.wymin)

        # Calculate 1 pixel in world coordinates
        self.xpix = 1 / self.xscale
        self.ypix = 1 / self.yscale

    def w_to_d(self, wx, wy):
        """ Map a point from world to device coordinates """
        dx = (wx - self.wxmin) * self.xscale + self.dxmin
        dy = (wy - self.wymin) * self.yscale + self.dymin
        return dx, dy

    def clear(self):
        self.canvas.delete(tk.ALL)

    def wdraw_line(self, wx0, wy0, wx1, wy1, color, arrow):
        """ Draw a line in world coordinates """
        dx0, dy0 = self.w_to_d(wx0, wy0)
        dx1, dy1 = self.w_to_d(wx1, wy1)
        self.canvas.create_line(dx0, dy0, dx1, dy1, fill=color, arrow=arrow)

    def wdraw_axes(self, xtic_spacing, ytic_spacing, tic_hgt, tic_wid, do_draw_text, color):
        """ Draw coordinate axes """
        self.wdraw_line(self.wxmin, 0, self.wxmax, 0, color, arrow=tk.BOTH)
        self.wdraw_line(0, self.wymin, 0, self.wymax, color, arrow=tk.BOTH)

        startx = xtic_spacing * int((self.wxmin - xtic_spacing) / xtic_spacing)
        x = startx
        while x < self.wxmax:
            if (abs(x) > 0.01):
                dx0, dy0 = self.w_to_d(x, tic_hgt)
                dx1, dy1 = self.w_to_d(x, -tic_hgt)
                self.canvas.create_line(dx0, dy0, dx1, dy1, fill=color)
                if do_draw_text:
                    self.canvas.create_text(dx1, dy1, text=str(x), fill=color, anchor=tk.N)
            x += xtic_spacing

        starty = ytic_spacing * int((self.wymin - ytic_spacing) / ytic_spacing)
        y = starty
        while y < self.wymax:
            if (abs(y) > 0.01):
                dx0, dy0 = self.w_to_d(tic_wid, y)
                dx1, dy1 = self.w_to_d(-tic_wid, y)
                self.canvas.create_line(dx0, dy0, dx1, dy1, fill=color)
                if do_draw_text:
                    self.canvas.create_text(dx1, dy1, text=str(y), fill=color, anchor=tk.E)
            y += ytic_spacing

    def wdraw_polyline(self, wcoords, color):
        """ Draw a connected series of points in world coordinates """
        dpoints = []
        for i in range(0, len(wcoords), 2):
            dpoints += self.w_to_d(wcoords[i], wcoords[i + 1])
        self.canvas.create_line(dpoints, fill=color)

    def wdraw_polygon(self, wcoords, fill, outline):
        """ Draw a polygon in world coordinates """
        dpoints = []
        for i in range(0, len(wcoords), 2):
            dpoints += self.w_to_d(wcoords[i], wcoords[i + 1])
        self.canvas.create_polygon(dpoints, fill=fill, outline=outline)

    def wdraw_rotated_text(self, wx, wy, text, angle, color, font):
        """ Draw a rotated text at the indicated position in world coordinates."""
        dx, dy = self.w_to_d(wx, wy)
        self.canvas.create_text(dx, dy, text=text, angle=angle, fill=color, font=font)

    def wdraw_function(self, func, color, wxmin, wxmax, step_x):
        """ draw a function """
        points = []
        x = wxmin
        while x <= wxmax:
            points.append(x)
            points.append(func(x))
            x += step_x
        self.wdraw_polyline(points, color)

    def wdraw_circle(self, wx, wy, dradius, fill, outline):
        """ Draw an circle at the indicated position in world coordinates """
        dx0, dy0 = self.w_to_d(wx, wy)
        self.canvas.create_oval(dx - dradius, dy - dradius, dx + dradius, dy + dradius, fill=fill, outline=outline)

    def wdraw_oval(self, wx0, wy0, wx1, wy1, fill, outline):
        """ Draw an oval at the indicated position in world coordinates """
        dx0, dy0 = self.w_to_d(wx0, wy0)
        dx1, dy1 = self.w_to_d(wx1, wy1)
        self.canvas.create_oval(dx0, dy0, dx1, dy1, fill=fill, outline=outline)

    def wdraw_rectangle(self, wx0, wy0, wx1, wy1, fill, outline):
        """ Draw a rectangle at the indicated position in world coordinates """
        dx0, dy0 = self.w_to_d(wx0, wy0)
        dx1, dy1 = self.w_to_d(wx1, wy1)
        self.canvas.create_rectangle(dx0, dy0, dx1, dy1, fill=fill, outline=outline)


def integrate_adaptive_midpoint(function, xmin, xmax, intervals, max_error):
    """ Integrate by using the trapezoid rule """
    dx = (xmax - xmin) / intervals
    total = 0

    # perform the integration
    x = xmin
    for interval in range(intervals):
        # add the area in the trapezoid for this slice
        total += slice_area(function, x, x + dx, max_error)

        # move to the next slice
        x += dx

    return total


def slice_area(function, x1, x2, max_error):
    # calculate function at the endpoints and midpoints
    y1 = function(x1)
    y2 = function(x2)
    xm = (x1 + x2) / 2
    ym = function(xm)

    # calculate the areas of sclices and large portion itself
    large = (x2 - x1) * (y1 + y2) / 2
    first = (xm - x1) * (y1 + ym) / 2
    second = (x2 - xm) * (y2 + ym) / 2
    both = first + second

    # calculate the error
    error = (both - large) / large

    # see if the error is small
    if abs(error) < max_error:
        return both

    # error is big, divide it into two slices
    return slice_area(function, x1, xm, max_error) + slice_area(function, xm, x2, max_error)


class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('Trapezoidal Rule (Addy)')
        self.window.protocol('WM_DELETE_WINDOW', self.kill_callback)
        self.window.geometry('400x510')

        label = tk.Label(self.window, text="y = 1 + x + sin(2 * x)")
        label.pack(padx=5, pady=2, side=tk.TOP)

        self.canvas = tk.Canvas(self.window, width=280, height=280, relief=tk.RIDGE, bd=5, highlightthickness=0,
                                bg='white')
        self.canvas.pack(padx=5, pady=2, side=tk.TOP, fill=tk.X)

        frame = tk.Frame()
        frame.pack(side=tk.TOP)
        label = tk.Label(frame, text='X:')
        label.grid(padx=5, pady=2, row=0, column=0)
        self.xmin_entry = tk.Entry(frame, width=5, justify=tk.RIGHT)
        self.xmin_entry.grid(padx=5, pady=2, row=0, column=1)
        self.xmin_entry.insert(0, '0')
        label = tk.Label(frame, text='to')
        label.grid(padx=5, pady=2, row=0, column=2)
        self.xmax_entry = tk.Entry(frame, width=5, justify=tk.RIGHT)
        self.xmax_entry.grid(padx=5, pady=2, row=0, column=3)
        self.xmax_entry.insert(0, '5')

        label = tk.Label(frame, text='Initial Intervals:')
        label.grid(padx=5, pady=2, row=1, column=0, columnspan=3)
        self.intervals_entry = tk.Entry(frame, width=5, justify=tk.RIGHT)
        self.intervals_entry.grid(padx=5, pady=2, row=1, column=3)
        self.intervals_entry.insert(0, '5')

        label = tk.Label(frame, text='Max Slice Error:')
        label.grid(padx=5, pady=2, row=2, column=0, columnspan=3)
        self.max_error_entry = tk.Entry(frame, width=5, justify=tk.RIGHT)
        self.max_error_entry.grid(padx=5, pady=2, row=2, column=3)
        self.max_error_entry.insert(0, '1')
        label = tk.Label(frame, text='%')
        label.grid(padx=1, pady=2, row=2, column=4)

        integrate_button = tk.Button(self.window, text='Integrate', width=10, command=self.integrate)
        integrate_button.pack(padx=5, pady=2, side=tk.TOP)

        frame = tk.Frame()
        frame.pack(side=tk.TOP)
        label = tk.Label(frame, text='Est. Area:')
        label.grid(padx=5, pady=2, row=0, column=0)
        self.est_area_entry = tk.Entry(frame, width=16, justify=tk.RIGHT)
        self.est_area_entry.grid(padx=5, pady=2, row=0, column=1)

        label = tk.Label(frame, text='True Area:')
        label.grid(padx=5, pady=2, row=1, column=0)
        self.true_area_entry = tk.Entry(frame, width=16, justify=tk.RIGHT)
        self.true_area_entry.grid(padx=5, pady=2, row=1, column=1)
        label = tk.Label(frame, text='% Err:')
        label.grid(padx=5, pady=2, row=1, column=2)
        self.pct_error_entry = tk.Entry(frame, width=10, justify=tk.RIGHT)
        self.pct_error_entry.grid(padx=5, pady=2, row=1, column=3)

        label = tk.Label(frame, text='Intervals:')
        label.grid(padx=5, pady=2, row=2, column=0)
        self.num_intervals_entry = tk.Entry(frame, width=16, justify=tk.RIGHT)
        self.num_intervals_entry.grid(padx=5, pady=2, row=2, column=1)

        # make the DrawingCanvas
        self.wxmin = -1
        self.wymin = -1
        self.wxmax = 7
        self.wymax = 7
        self.drawing_canvas = DrawingCanvas(self.canvas, self.wxmin, self.wymin, self.wxmax, self.wymax, 0, True)

        # bind some keys
        self.window.bind('<Return>', (lambda e, button=integrate_button: integrate_button.invoke()))

        # Alt+F4 closes this window not python shell
        self.xmin_entry.focus_force()
        self.window.mainloop()

    def kill_callback(self):
        self.window.destroy()

    def integrate(self):
        """ perform the integration """
        # get parameters
        xmin = float(self.xmin_entry.get())
        xmax = float(self.xmax_entry.get())

        intervals = int(self.intervals_entry.get())
        max_error = float(self.max_error_entry.get()) / 100

        # integrate
        est_area = integrate_adaptive_midpoint(self.f, xmin, xmax, intervals, max_error)
        self.est_area_entry.delete(0, tk.END)
        self.est_area_entry.insert(0, f'{est_area:,.12}')

        # display the true area and percent error
        true_area = self.anti_derivative_f(xmax) - self.anti_derivative_f(xmin)
        self.true_area_entry.delete(0, tk.END)
        self.true_area_entry.insert(0, f'{true_area:,.12}')

        pct_error = 100 * (est_area - true_area) / true_area
        self.pct_error_entry.delete(0, tk.END)
        self.pct_error_entry.insert(0, f'{pct_error:,.4} %')

        # draw the graph
        self.draw_graph()

        # display the number of intervals used
        self.num_intervals_entry.delete(0, tk.END)
        self.num_intervals_entry.insert(0, f'{self.num_intervals}')

    def f(self, x):
        """ The function we will integrate """
        return 1 + x + math.sin(2.0 * x)

    def anti_derivative_f(self, x):
        """ anti-derivative of the function """
        return x + x * x / 2.0 - math.cos(2.0 * x) / 2.0

    def draw_graph(self):
        """ draw the graph. Just for visualisation """
        """ make the basic image and reset the area counts """
        self.drawing_canvas.clear()

        # get parameters
        xmin = float(self.xmin_entry.get())
        xmax = float(self.xmax_entry.get())

        intervals = int(self.intervals_entry.get())
        max_error = float(self.max_error_entry.get()) / 100

        # fill and draw rectangles
        self.draw_trapezoids(self.f, xmin, xmax, intervals, max_error, 'lightblue', 'blue')

        # draw axes
        self.drawing_canvas.wdraw_axes(1, 1, 0.1, 0.1, True, 'red')

        # draw the function
        xpix = self.drawing_canvas.xpix
        self.drawing_canvas.wdraw_function(self.f, 'green', self.wxmin, self.wxmax, xpix)

    def draw_trapezoids(self, function, xmin, xmax, intervals, max_error, fill, outline):
        """ draw the integration trapezoids """
        self.num_intervals = 0
        dx = (xmax - xmin) / intervals

        # perform the integration
        x = xmin
        for interval in range(intervals):
            # draw this slice
            self.draw_one_trapezoid(function, x, x + dx, max_error, fill, outline)

            # move to the next slice
            x += dx

    def draw_one_trapezoid(self, function, x1, x2, max_error, fill, outline):
        # calculate function at the endpoint and midpoint
        y1 = function(x1)
        y2 = function(x2)
        xm = (x1 + x2) / 2
        ym = function(xm)

        # calculate the areas of the large trapezoid and its slices
        large = (x2 - x1) * (y1 + y1) / 2
        first = (xm - x1) * (ym + y1) / 2
        second = (x2 - xm) * (y2 + ym) / 2
        both = first + second

        # calculate error
        error = (both - large) / large

        # see if error is small enough
        if abs(error) < max_error:
            # draw the trapezoid
            coords = [x1, 0, x1, y1, x2, y2, x2, 0]
            self.drawing_canvas.wdraw_polygon(coords, fill, outline)
            self.num_intervals += 1
            return

        # the error is too big, divide the slice
        self.draw_one_trapezoid(function, x1, xm, max_error, fill, outline)
        self.draw_one_trapezoid(function, xm, x2, max_error, fill, outline)


if __name__ == '__main__':
    app = App()