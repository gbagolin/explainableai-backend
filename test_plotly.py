import plotly.graph_objects as go
import plotly.express as px

animals = ['Tiger left', 'Tiger right']

colors_map = {
    'Not acceptable': 'rgb(255,255,255)',
    'Accceptable': 'rgb(255,255,0)'
}

fig = go.Figure(data=[
    px.bar(x=animals, y=[0.5, 0.8], color_discrete_map=colors_map),
    px.bar(x=animals, y=[0.5, 0.2])
])
# Change the bar mode
fig.update_layout(barmode='stack')
# fig.update_traces(marker_color=colors, marker_line_color='rgb(8,48,107)',
#                   marker_line_width=1.5, opacity=0.6)
fig.show()



fig = px.bar(x=["a","b","c"], y=[1,3,2], color=["red", "goldenrod", "#00D"], color_discrete_map="identity")
fig.show()
