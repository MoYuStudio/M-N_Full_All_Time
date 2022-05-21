
import math

from bokeh.plotting import figure, output_file, show
 
output_file('src_html/offset.html')
 
p = figure(plot_width=700, plot_height=700)

N = 100

B = (math.degrees(360)*(N-81))/364

E = 9.87*math.sin(2*B) - 7.53*math.cos(B) - 1.5*math.sin(B)

x = []
y = []

for i in range(N):
    N -= 1
    B = (math.degrees(360)*(N-81))/364
    E = 9.87*math.sin(2*B) - 7.53*math.cos(B) - 1.5*math.sin(B)
    x.append(i)
    y.append(E)

# add a patch renderer with an alpha an line width
p.line(x, y, line_width=2, alpha=0.5)
 
show(p)
