import streamlit as st
import replicate
import os
from PIL import Image
import requests
from io import BytesIO

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Home Renovator", page_icon="🏠")

st.title("🏠 AI Home Renovator Chatbot")
st.markdown("Upload a photo of your house and tell the AI what to change!")

# --- SIDEBAR: API KEY HANDLING ---
# In production, you would set this in your environment variables.
# For now, we allow the user (or you) to enter it to test.
api_token = st.sidebar.text_input("Replicate API Token", type="password")

if api_token:
    os.environ["REPLICATE_API_TOKEN"] = api_token

# --- STEP 1: UPLOAD IMAGE ---
uploaded_file = st.file_uploader("Upload an image of a house...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the original image
    image = Image.open(uploaded_file)
    st.image(image, caption='Original House', use_container_width=True)

    # --- STEP 2: USER PROMPT ---
    # This is the "Chatbot" aspect
    prompt = st.text_input("What would you like to change?", placeholder="Make the roof black")

    # --- STEP 3: PROCESS IMAGE ---
    if st.button("Generate Renovation"):
        if not api_token:
            st.error("Please enter your API Token in the sidebar.")
        elif not prompt:
            st.error("Please enter a prompt description.")
        else:
            with st.spinner('AI is working on your renovation... this may take a few seconds...'):
                try:
                    # We save the uploaded file temporarily to send to Replicate
                    # (Replicate expects a file handle or URL)
                    
                    # NOTE: I am using 'timothybrooks/instruct-pix2pix' which is excellent for 
                    # editing images based on text. 
                    # If you want to use your specific model "google/nano-banana", change the ID below.
                    
                    model_id = "timothybrooks/instruct-pix2pix:30c1d0b916a6f8efce20493f5d61ee27491b89aaa70228af9ea01f30c131a317"
                    
                    output = replicate.run(
                        model_id,
                        input={
                            "image": uploaded_file,
                            "prompt": prompt,
                            "image_guidance_scale": 1.5, # Controls how much the original image is preserved
                        }
                    )

                    # --- STEP 4: DISPLAY RESULT ---
                    # Replicate returns a URL (or list of URLs)
                    if isinstance(output, list):
                        result_url = output[0]
                    else:
                        result_url = output

                    st.success("Renovation Complete!")
                    st.image(result_url, caption="Renovated House", use_container_width=True)
                    
                    # Add a download button
                    response = requests.get(result_url)
                    st.download_button(
                        label="Download Image",
                        data=response.content,
                        file_name="renovated_house.jpg",
                        mime="image/jpeg"
                    )

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")