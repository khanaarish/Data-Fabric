import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import seaborn as sns
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pickle
from st_ant_statistic import st_ant_statistic

# Load the service account credentials
credentials = ServiceAccountCredentials.from_json_keyfile_name('third-389406-64c6878c09d9.json', ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])

# Authenticate with the Google Sheets API
gc = gspread.authorize(credentials)

st.set_page_config(layout='wide')
# making of sidebar
with st.sidebar:
    
    selected = option_menu('Tiranga Textiles',
                           
                           ['Taka Production',
                            'Karigar Performance','Prediction'],
                           
                           icons = ['activity', 'bi bi-person-gear', 'bi bi-crosshair'],
                           
                           default_index=0)

if (selected == 'Taka Production'):

    st.title('Production of Taka By Date')


    # This code is for adding production entry directly from app

    # client = gspread.authorize(credentials)
    # sheet_names = 'Tiranga Tex To Krishna Tex(24 looms)'
    # sheets = client.open(sheet_names).sheet1

    # # Get the inputs from the Streamlit app
    # dates = st.date_input('Select Date')
    # chota_panna = st.number_input('Enter Chota Panna')
    # bada_panna = st.number_input('Enter Bada Panna')
    # total = st.number_input('Enter Total')
    # # total = chota_panna + bada_panna

    # # Create a new row entry for the Karigar
    # new_row = [str(dates), chota_panna, bada_panna, total]

    # # Append the new row to the Google Sheet
    # sheets.append_row(new_row)

    # # Display a success message
    # st.success('Production entry added successfully!')

    # Open the Google Sheet by its name
    sheet_name = 'Tiranga Tex To Krishna Tex(24 looms)'
    sheet = gc.open(sheet_name).sheet1

    # Get all values from the Google Sheet
    data = sheet.get_all_values()

    # Convert the data to a Pandas DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])

    # Display the DataFrame
    # st.dataframe(df)

    from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, JsCode 

    
    onRowDragEnd = JsCode("""
    function onRowDragEnd(e) {
        console.log('onRowDragEnd', e);
    }
    """)
    
    getRowNodeId = JsCode("""
    function getRowNodeId(data) {
        return data.id
    }
    """)
    
    onGridReady = JsCode("""
    function onGridReady() {
        immutableStore.forEach(
            function(data, index) {
                data.id = index;
                });
        gridOptions.api.setRowData(immutableStore);
        }
    """)
    
    onRowDragMove = JsCode("""
    function onRowDragMove(event) {
        var movingNode = event.node;
        var overNode = event.overNode;
    
        var rowNeedsToMove = movingNode !== overNode;
    
        if (rowNeedsToMove) {
            var movingData = movingNode.data;
            var overData = overNode.data;
    
            immutableStore = newStore;
    
            var fromIndex = immutableStore.indexOf(movingData);
            var toIndex = immutableStore.indexOf(overData);
    
            var newStore = immutableStore.slice();
            moveInArray(newStore, fromIndex, toIndex);
    
            immutableStore = newStore;
            gridOptions.api.setRowData(newStore);
    
            gridOptions.api.clearFocusedCell();
        }
    
        function moveInArray(arr, fromIndex, toIndex) {
            var element = arr[fromIndex];
            arr.splice(fromIndex, 1);
            arr.splice(toIndex, 0, element);
        }
    }
    """)
    
    
    data = df #pd.read_csv('generic`Preformatted text`.csv', sep=';', decimal=',', encoding='latin-1').head(10)
    
    gb = GridOptionsBuilder.from_dataframe(data)
    gb.configure_default_column(rowDrag = False, rowDragManaged = True, rowDragEntireRow = False, rowDragMultiRow=True)
    gb.configure_column('bloco', rowDrag = True, rowDragEntireRow = True)
    gb.configure_grid_options(rowDragManaged = True, onRowDragEnd = onRowDragEnd, deltaRowDataMode = True, getRowNodeId = getRowNodeId, onGridReady = onGridReady, animateRows = True, onRowDragMove = onRowDragMove)
    gridOptions = gb.build()
    
    data = AgGrid(data,
                gridOptions=gridOptions,
                allow_unsafe_jscode=True,
                update_mode=GridUpdateMode.MANUAL
    )
   
    # Get column names from the DataFrame
    column_names = df.columns.tolist()

    # Add a selectbox for x-axis column selection
    x_axis_column = st.sidebar.selectbox('Select X-Axis Column', column_names, index=1)

    # Add a selectbox for y-axis column selection
    y_axis_column = st.sidebar.selectbox('Select Y-Axis Column', column_names, index=4)
    
    graph_names = ["Line Chart", "Scatter Plot", "Box Plot", "Area Chart"]
    # Add a selectbox for Graph type
    graph_type = st.sidebar.selectbox("Choose a Graph", graph_names, index=0)
    
    if (graph_type == "Line Chart"):
        
        fig = go.Figure(data=go.Scatter(x=df[x_axis_column], y=df[y_axis_column], mode='lines', line=dict(width=5)))
        # Customize the chart layout
        fig.update_layout(showlegend=True, hovermode='closest', xaxis_title=x_axis_column, yaxis_title=y_axis_column)
        
        # Display the line chart using Streamlit
        st.plotly_chart(fig)

    # different graphs
    elif (graph_type == "Scatter Plot"):
    # Create the scatter plot trace
        scatter_trace = go.Scatter(x=df[x_axis_column], y=df[y_axis_column], mode='markers')
    
        # Customize the chart layout
        layout = go.Layout(
            title='Scatter Plot',
            xaxis=dict(title='X-axis'),
            yaxis=dict(title='Y-axis'),
            showlegend=True
        )
    
        # Create the figure
        fig = go.Figure(data=[scatter_trace], layout=layout)
    
        # Display the scatter plot using Streamlit
        st.plotly_chart(fig)
    

    # Create the box plot trace
    elif (graph_type == "Box Plot"):
        box_trace = go.Box(x=df[x_axis_column], y=df[y_axis_column])
    
        # Customize the chart layout
        layout = go.Layout(
            title='Box Plot',
            xaxis=dict(title='X-axis'),
            yaxis=dict(title='Y-axis'),
            showlegend=True
        )
    
        # Create the figure
        fig = go.Figure(data=[box_trace], layout=layout)
    
        # Display the box plot using Streamlit
        st.plotly_chart(fig)
    # Create the area chart trace
    elif (graph_type == "Area Chart"):
        
        area_trace = go.Scatter(x=df[x_axis_column], y=df[y_axis_column], fill='tozeroy')
    
        # Customize the chart layout
        layout = go.Layout(
            title='Area Chart',
            xaxis=dict(title='X-axis'),
            yaxis=dict(title='Y-axis'),
            showlegend=True
        )
    
        # Create the figure
        fig = go.Figure(data=[area_trace], layout=layout)
    
        # Display the area chart using Streamlit
        st.plotly_chart(fig)
    

if (selected == 'Karigar Performance'):

    st.title('Karigar Performance By Date')

    # Open the Google Sheet by its name
    sheet_name = 'Karigar Performance(24 looms)'
    sheet = gc.open(sheet_name).sheet1
    sheet3 = gc.open(sheet_name).get_worksheet(1)
    
    # Get all values from the Google Sheet
    data = sheet.get_all_values()
    beta = sheet3.get_all_values()

    # Convert the data to a Pandas DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])
    fd = pd.DataFrame(beta[1:], columns=beta[0])

    # Display the DataFrame

    st.header("Performance")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
            "Naseem",
            fd['Total (Naseem)'].dropna().iloc[-1],
            fd['Total (Naseem)'].dropna().iloc[-1],
            help="Last 15 Days Production",
        )
    col2.metric(
            "Prem",
            fd['Total(Prem)'].dropna().iloc[-1],
            help="Last 15 Days Production",
        )
    col3.metric(
            "Abdullah",
            fd['Total(Abdullah)'].dropna().iloc[-1],
            help="Last 15 Days Production",
        )
    col4.metric(
            "Total of All",
            fd['Total of All'].dropna().iloc[-1],
            help="Total of Last 15 Days Production",
        )
    
    code = ''' Is the best performer'''
    st.code(code, language='python')
    st.write("")

    # st.title('3D Graph with Plotly')

    # # Create a 3D scatter plot
    # fig = go.Figure(data=[go.Scatter3d(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], mode='markers', marker=dict(size=10))])

    # # Show the plot in Streamlit app
    # st.plotly_chart(fig)

    # st.dataframe(df)
    from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, JsCode 

    
    onRowDragEnd = JsCode("""
    function onRowDragEnd(e) {
        console.log('onRowDragEnd', e);
    }
    """)
    
    getRowNodeId = JsCode("""
    function getRowNodeId(data) {
        return data.id
    }
    """)
    
    onGridReady = JsCode("""
    function onGridReady() {
        immutableStore.forEach(
            function(data, index) {
                data.id = index;
                });
        gridOptions.api.setRowData(immutableStore);
        }
    """)
    
    onRowDragMove = JsCode("""
    function onRowDragMove(event) {
        var movingNode = event.node;
        var overNode = event.overNode;
    
        var rowNeedsToMove = movingNode !== overNode;
    
        if (rowNeedsToMove) {
            var movingData = movingNode.data;
            var overData = overNode.data;
    
            immutableStore = newStore;
    
            var fromIndex = immutableStore.indexOf(movingData);
            var toIndex = immutableStore.indexOf(overData);
    
            var newStore = immutableStore.slice();
            moveInArray(newStore, fromIndex, toIndex);
    
            immutableStore = newStore;
            gridOptions.api.setRowData(newStore);
    
            gridOptions.api.clearFocusedCell();
        }
    
        function moveInArray(arr, fromIndex, toIndex) {
            var element = arr[fromIndex];
            arr.splice(fromIndex, 1);
            arr.splice(toIndex, 0, element);
        }
    }
    """)
    
    
    data = df #pd.read_csv('generic`Preformatted text`.csv', sep=';', decimal=',', encoding='latin-1').head(10)
    
    gb = GridOptionsBuilder.from_dataframe(data)
    gb.configure_default_column(rowDrag = False, rowDragManaged = True, rowDragEntireRow = False, rowDragMultiRow=True)
    gb.configure_column('bloco', rowDrag = True, rowDragEntireRow = True)
    gb.configure_grid_options(rowDragManaged = True, onRowDragEnd = onRowDragEnd, deltaRowDataMode = True, getRowNodeId = getRowNodeId, onGridReady = onGridReady, animateRows = True, onRowDragMove = onRowDragMove)
    gridOptions = gb.build()
    
    data = AgGrid(data,
                gridOptions=gridOptions,
                allow_unsafe_jscode=True,
                update_mode=GridUpdateMode.MANUAL
    )
    
    # st.write(data['data'])
    
     # Get column names from the DataFrame
    column_names = df.columns.tolist()

    # Add a selectbox for x-axis column selection
    x_axis_column = st.sidebar.selectbox('Select X-Axis Column', column_names, index=1)

    # Add a selectbox for y-axis column selection
    y_axis_column = st.sidebar.selectbox('Select Y-Axis Column', column_names, index=2)
    y_axis_column_2 = st.sidebar.selectbox('Select Y-Axis Column 2', column_names)
    y_axis_column_3 = st.sidebar.selectbox('Select Y-Axis Column 3', column_names)
    
    graph_names = ["Line Chart", "Scatter Plot", "Box Plot", "Area Chart", "Pie Chart"]
    # Add a selectbox for Graph type
    graph_type = st.sidebar.selectbox("Choose a Graph", graph_names, index=0)
    
    if (graph_type == "Line Chart"):
        
        #  Create the line chart figure
        fig = go.Figure()

        # Add the first y-axis column
        fig.add_trace(go.Scatter(x=df[x_axis_column], y=df[y_axis_column], mode='lines', name=y_axis_column))

        # Add the second y-axis column
        fig.add_trace(go.Scatter(x=df[x_axis_column], y=df[y_axis_column_2], mode='lines', name=y_axis_column_2))
        fig.add_trace(go.Scatter(x=df[x_axis_column], y=df[y_axis_column_3], mode='lines', name=y_axis_column_3))
        # Customize the chart layout
        fig.update_layout(showlegend=True, hovermode='closest', xaxis_title=x_axis_column, yaxis_title="Metre")
        
        # Display the line chart using Streamlit
        st.plotly_chart(fig)
        

    # different graphs
    elif (graph_type == "Scatter Plot"):
    # Create the scatter plot trace
        scatter_trace = go.Scatter(x=df[x_axis_column], y=df[y_axis_column], mode='markers')
    
        # Customize the chart layout
        layout = go.Layout(
            title='Scatter Plot',
            xaxis=dict(title='X-axis'),
            yaxis_title=y_axis_column,
            showlegend=True
        )
    
        # Create the figure
        fig = go.Figure(data=[scatter_trace], layout=layout)
    
        # Display the scatter plot using Streamlit
        st.plotly_chart(fig)
    

    # Create the box plot trace
    elif (graph_type == "Box Plot"):
        box_trace = go.Box(x=df[x_axis_column], y=df[y_axis_column])
    
        # Customize the chart layout
        layout = go.Layout(
            title='Box Plot',
            xaxis=dict(title='X-axis'),
            yaxis=dict(title='Y-axis'),
            showlegend=True
        )
    
        # Create the figure
        fig = go.Figure(data=[box_trace], layout=layout)
    
        # Display the box plot using Streamlit
        st.plotly_chart(fig)
    # Create the area chart trace
    elif (graph_type == "Area Chart"):
        
        area_trace = go.Scatter(x=df[x_axis_column], y=df[y_axis_column], fill='tozeroy')
    
        # Customize the chart layout
        layout = go.Layout(
            title='Area Chart',
            xaxis=dict(title='X-axis'),
            yaxis=dict(title='Y-axis'),
            showlegend=True
        )
    
        # Create the figure
        fig = go.Figure(data=[area_trace], layout=layout)
    
        # Display the area chart using Streamlit
        st.plotly_chart(fig)

    elif (graph_type == "Pie Chart"):
    
        # Prepare the data for the Pie Chart
        # Assuming df[y_axis_column] contains categorical data and df[x_axis_column] contains the corresponding values
        pie_data = df.groupby(y_axis_column)[x_axis_column].sum().reset_index()
        
        # Create the Pie Chart trace
        pie_trace = go.Pie(labels=pie_data[y_axis_column], values=pie_data[x_axis_column])
        
        # Customize the chart layout
        layout = go.Layout(
            title='Pie Chart',
            showlegend=True
        )
        
        # Create the figure
        fig = go.Figure(data=[pie_trace], layout=layout)
        
        # Display the pie chart using Streamlit
        st.plotly_chart(fig)

# Assuming your model is saved in 'model.pkl' in the same directory
with open('prod.pkl', 'rb') as file:
    model = pickle.load(file)

if selected == 'Prediction':
    st.title('Predict the Production on 10th and 25th')

    # Taking user inputs
    year = st.number_input('Year', min_value=2020, max_value=2030, value=2026)
    month = st.number_input('Month', min_value=1, max_value=12, value=11)
    day = st.selectbox('Day',[10,25])
    taka = st.number_input('Taka', min_value=1, value=2)


    
    
    
    
    # Create a button for prediction
    if st.button('Predict Production'):
        input_data = {'Year': [year],
                      'Month': [month],
                      'Day': [day],
                      'Taka': [taka]}
        
        input_df = pd.DataFrame(input_data)
        
        # Making a prediction
        predicted_total = model.predict(input_df)
        
        # Display the predicted total
        st.write(f"Predicted 'Total of 15 days': {predicted_total[0]}")
        st.write(f"Predicted Meter of Fabric made: {predicted_total[0]*110}")
        meter = predicted_total*110
        rev = meter*3.80
        st.write(f"Predicted Revenue at this production is ': {rev} Rupees")

        # st_ant_statistic(
        # title="Revenue",
        # value=rev,
        # prefix="<i class='fa fa-check' aria-hidden='true'></i>",
        # precision=2,
        # decimalSeperator=",",
        # card=True,
        # cardStyle={"width":"25%", "background-color":"#f5f5f5", "border-radius":"10px", "border-color":"black", "margin":"10px"},
        # height=200)
        




    