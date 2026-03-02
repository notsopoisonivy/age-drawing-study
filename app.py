# save this as app.py
import streamlit as st
import pandas as pd
import numpy as np
import time
import json

st.title("Age vs Motor Control Study")

# Participant info
participant_id = st.text_input("Participant ID")
age_group = st.selectbox("Age Group", ["Enter your age"])

if participant_id and age_group:
    st.write("Instructions:")
    st.write("- Use your trackpad only")
    st.write("- Complete each drawing and typing task in order")
    
    # -------------------
    # Drawing Section
    # -------------------
    st.subheader("Drawing Tasks")
    
    drawing_tasks = ["Draw a straight horizontal line", 
                     "Draw a circle", 
                     "Sign your name naturally"]
    
    all_drawing_data = []
    
    for task in drawing_tasks:
        st.write(task)
        canvas_data = st.empty()
        
        # Use Streamlit's built-in drawing tool
        from streamlit_drawable_canvas import st_canvas
        
        canvas_result = st_canvas(
            fill_color="rgba(0, 0, 0, 0)", 
            stroke_width=2,
            stroke_color="black",
            background_color="white",
            height=400,
            width=700,
            drawing_mode="freedraw",
            key=task
        )
        
        if canvas_result.json_data is not None:
            # json_data contains all points
            drawing_points = json.loads(canvas_result.json_data)
            # add participant info + task
            for obj in drawing_points.get("objects", []):
                if obj["type"] == "path":
                    for point in obj["path"]:
                        x, y = point[1], point[2]
                        timestamp = time.time()
                        all_drawing_data.append([participant_id, age_group, task, "draw_point", x, y, timestamp])
    
    st.success("Drawing tasks complete!")

    # -------------------
    # Typing Section
    # -------------------
    st.subheader("Typing Task")
    typing_text = st.text_input("Type this sentence:", value="The quick brown fox jumps over the lazy dog")
    st.write("You typed:", typing_text)
    
    all_typing_data = []
    
    # Record timing on key press is tricky in Streamlit.
    # Workaround: record submission timestamp
    submit_button = st.button("Submit Typing Task")
    if submit_button:
        timestamp = time.time()
        for i, char in enumerate(typing_text):
            all_typing_data.append([participant_id, age_group, "Typing", "key_press", char, timestamp])
        st.success("Typing task submitted!")
    
    # # -------------------
    # # Save CSV
    # # -------------------
    # save_button = st.button("Save Data to CSV")
    # if save_button:
    #     drawing_df = pd.DataFrame(all_drawing_data, columns=["participant_id", "age_group", "task", "event_type", "x", "y", "timestamp"])
    #     typing_df = pd.DataFrame(all_typing_data, columns=["participant_id", "age_group", "task", "event_type", "key", "timestamp"])
        
    #     drawing_df.to_csv(f"{participant_id}_drawing.csv", index=False)
    #     typing_df.to_csv(f"{participant_id}_typing.csv", index=False)
        
    #     st.success("Data saved locally as CSV!")
    #     st.write("You can now use these CSVs for feature extraction.")

    # -------------------
# Save CSV / Download
# -------------------
save_button = st.button("Save Data to CSV")
if save_button:
    
    st.write("Once you finish all tasks, click the button below to download your data.")
    st.write("The file will include your participant ID and age group in the filename.")
    
    # Create DataFrames
    drawing_df = pd.DataFrame(all_drawing_data, columns=["participant_id", "age_group", "task", "event_type", "x", "y", "timestamp"])
    typing_df = pd.DataFrame(all_typing_data, columns=["participant_id", "age_group", "task", "event_type", "key", "timestamp"])
    
    # Combine drawing + typing into one CSV
    # Fill missing columns with NaN
    drawing_df_typing_compatible = drawing_df.copy()
    drawing_df_typing_compatible["key"] = np.nan  # typing column placeholder

    typing_df_drawing_compatible = typing_df.copy()
    typing_df_drawing_compatible["x"] = np.nan
    typing_df_drawing_compatible["y"] = np.nan

    combined_df = pd.concat([drawing_df_typing_compatible, typing_df_drawing_compatible], ignore_index=True)
    
    # Generate dynamic filename
    file_name = f"participant_{participant_id}_{age_group}.csv"
    
    # Streamlit download button
    st.download_button(
        label="Submit / Download Your Data",
        data=combined_df.to_csv(index=False),
        file_name=file_name,
        mime="text/csv"
    )
    
    st.success(f"Data ready! CSV will be downloaded as: {file_name}")
    st.write("Please submit this file to the shared folder or via email as instructed by your study administrator.")