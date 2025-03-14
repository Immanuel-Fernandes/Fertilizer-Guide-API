import base64
from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
from markupsafe import Markup
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Fertilizer dictionary with recommendations
fertilizer_dic = {
    'NHigh': """<b>The Nitrogen Level of your soil is high and might give rise to weeds.</b>
        <br/> Please consider the following suggestions:
        <br/><br/> 1. <i>Add manure:</i> Adding manure is one of the simplest ways to amend your soil with nitrogen.
        <br/> 2. <i>Use coffee grinds:</i> Coffee grinds are a green compost material rich in nitrogen.
        <br/> 3. <i>Plant nitrogen-fixing plants:</i> Vegetables like peas, beans, and soybeans can increase nitrogen in your soil.
        <br/> 4. <i>Plant green manure crops:</i> Crops like cabbage, corn, and broccoli can improve nitrogen levels.
        <br/> 5. <i>Use mulch:</i> Wet grass, sawdust, and soft woods can be used as mulch to retain moisture and add nitrogen.
    """,
    'Nlow': """<b>The Nitrogen Level of your soil is low.</b>
        <br/> Please consider the following suggestions:
        <br/><br/> 1. <i>Add sawdust or fine woodchips:</i> These materials can absorb excess nitrogen and improve soil quality.
        <br/> 2. <i>Plant nitrogen-hungry plants:</i> Vegetables like tomatoes, corn, and cabbage thrive on nitrogen and can help deplete excess nitrogen.
        <br/> 3. <i>Water your soil:</i> Soaking your soil can leach nitrogen deeper, making it less available to plants.
        <br/> 4. <i>Add composted manure:</i> Composted manure can increase nitrogen levels in the soil.
        <br/> 5. <i>Use NPK fertilizers:</i> Fertilizers with high nitrogen content can boost nitrogen levels in the soil.
        <br/> 6. <i>Plant nitrogen-fixing plants:</i> Peas, beans, and other legumes can increase nitrogen naturally.
    """,
    'PHigh': """<b>The Phosphorous Level of your soil is high.</b>
        <br/> Please consider the following suggestions:
        <br/><br/> 1. <i>Avoid adding manure:</i> Manure can increase phosphorus levels. Limit its use to reduce phosphorus.
        <br/> 2. <i>Use phosphorus-free fertilizer:</i> Choose fertilizers with zero phosphorus to avoid adding more to the soil.
        <br/> 3. <i>Water your soil:</i> Soaking your soil can help leach excess phosphorus.
        <br/> 4. <i>Plant nitrogen-fixing vegetables:</i> Beans and peas can increase nitrogen without adding phosphorus.
        <br/> 5. <i>Use crop rotations:</i> Rotate crops to reduce high phosphorus levels.
    """,
    'Plow': """<b>The Phosphorous Level of your soil is low.</b>
        <br/> Please consider the following suggestions:
        <br/><br/> 1. <i>Add bone meal:</i> A fast-acting source of phosphorus.
        <br/> 2. <i>Use rock phosphate:</i> A slower but effective source of phosphorus.
        <br/> 3. <i>Apply phosphorus fertilizers:</i> Choose fertilizers with high phosphorus content.
        <br/> 4. <i>Add organic compost:</i> Quality compost can increase phosphorus levels.
        <br/> 5. <i>Use manure:</i> Manure is a natural source of phosphorus.
        <br/> 6. <i>Introduce clay soil:</i> Clay can help retain and fix phosphorus deficiencies.
        <br/> 7. <i>Ensure proper soil pH:</i> Maintain a pH of 6.0 to 7.0 for optimal phosphorus uptake.
    """,
    'KHigh': """<b>The Potassium Level of your soil is high.</b>
        <br/> Please consider the following suggestions:
        <br/><br/> 1. <i>Loosen the soil:</i> Deeply dig and water to dissolve excess potassium.
        <br/> 2. <i>Remove rocks:</i> Rocks can release potassium slowly; remove them if possible.
        <br/> 3. <i>Avoid potassium-rich fertilizers:</i> Use fertilizers with low potassium levels.
        <br/> 4. <i>Add calcium sources:</i> Crushed eggshells or seashells can balance potassium.
        <br/> 5. <i>Use NPK fertilizers with low K:</i> Choose fertilizers with balanced nutrients.
        <br/> 6. <i>Grow nitrogen-fixing cover crops:</i> Legumes can help without adding potassium.
    """,
    'Klow': """<b>The Potassium value of your soil is low.</b>
        <br/> Please consider the following suggestions:
        <br/><br/> 1. <i>Mix in potash:</i> Use muricate of potash or sulphate of potash.
        <br/> 2. <i>Try kelp meal or seaweed:</i> Natural sources of potassium.
        <br/> 3. <i>Use Sul-Po-Mag:</i> A mix of potassium, magnesium, and sulfur.
        <br/> 4. <i>Bury banana peels:</i> Natural potassium source for the soil.
        <br/> 5. <i>Use Potash fertilizers:</i> Choose fertilizers with high potassium content.
    """
}

# FastAPI app
app = FastAPI()

# Define input data model
class FertilizerRecommendationInput(BaseModel):
    crop_name: str
    N: int
    P: int
    K: int

# Function to generate graph
def generate_graph(n, p, k, nr, pr, kr):
    fig, ax = plt.subplots()
    categories = ['Nitrogen', 'Phosphorous', 'Potassium']
    required = [nr, pr, kr]
    current = [n, p, k]

    bar_width = 0.35
    index = range(len(categories))

    bar1 = ax.bar(index, required, bar_width, label='Required', color='#44AFF8')  # Blue color
    bar2_colors = ['#DAF7A6' if current[i] == required[i] else '#FF5733' for i in index]  # Green or Red
    bar2 = ax.bar([i + bar_width for i in index], current, bar_width, label='Current', color=bar2_colors)

    ax.set_xlabel('Nutrients')
    ax.set_ylabel('Levels')
    ax.set_title('Nutrient Levels for Crop')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(categories)
    ax.legend()

    # Convert the plot to PNG image and encode it to base64
    buffered = BytesIO()
    plt.savefig(buffered, format="png")
    buffered.seek(0)
    img_str = base64.b64encode(buffered.read()).decode("utf-8")
    return img_str

# Endpoint to get fertilizer recommendation
@app.post("/fertilizer-recommendation/")
async def fertilizer_recommendation(data: FertilizerRecommendationInput):
    # Sample fertilizer data
    df = pd.read_csv('Data/Fertilizer.csv')
    
    # Retrieve the required values for the crop
    try:
        nr = df[df['Crop'] == data.crop_name]['N'].iloc[0]
        pr = df[df['Crop'] == data.crop_name]['P'].iloc[0]
        kr = df[df['Crop'] == data.crop_name]['K'].iloc[0]
    except IndexError:
        return {"error": "Crop not found in the dataset"}

    n = nr - data.N
    p = pr - data.P
    k = kr - data.K

    # Prepare recommendations
    recommendations = []
    if n != 0:
        if n < 0:
            recommendations.append(fertilizer_dic['NHigh'])
        else:
            recommendations.append(fertilizer_dic['Nlow'])

    if p != 0:
        if p < 0:
            recommendations.append(fertilizer_dic['PHigh'])
        else:
            recommendations.append(fertilizer_dic['Plow'])

    if k != 0:
        if k < 0:
            recommendations.append(fertilizer_dic['KHigh'])
        else:
            recommendations.append(fertilizer_dic['Klow'])

    # Generate the graph
    graph_image_base64 = generate_graph(n, p, k, nr, pr, kr)

    # Combine recommendations and graph
    if recommendations:
        response = Markup("<br/><br/>".join(recommendations))
        return {"recommendations": response, "graph": graph_image_base64}
    else:
        return {"message": "Soil nutrients are optimal for the selected crop!", "graph": graph_image_base64}

# Run FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
