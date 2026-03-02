import streamlit as st
from PIL import Image
import base64
import datetime
import os

st.set_page_config(page_title="Web Photobooth", layout="wide")

st.title("📸 Photobooth")

# Timer selection
countdown = st.selectbox("Select Countdown", [3, 5], index=0)
shots = st.selectbox("Shots per Session", [3, 4], index=3)

st.write("Click the button below and allow camera access.")

# Webcam capture using JavaScript
capture_button = st.button("📷 Start Session")

if capture_button:
    st.write("Get ready!")
    # JavaScript for webcam capture
    capture_js = """
    <script>
    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
    const startCapture = async () => {
      const video = document.createElement('video');
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      video.play();
      document.body.appendChild(video);

      let images = [];
      for (let i = %COUNTDOWN%; i > 0; i--) {
        alert(i + "...");
        await sleep(1000);
      }

      for (let i = 0; i < %SHOTS%; i++) {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        images.push(canvas.toDataURL('image/jpeg'));
      }

      stream.getTracks().forEach(track => track.stop());
      video.remove();

      let streamlitImages = [];
      images.forEach((img) => {
        streamlitImages.push(img);
      });
      window.parent.postMessage({type: 'streamlit-webcam', images: streamlitImages}, "*");
    };
    startCapture();
    </script>
    """
    capture_code = capture_js.replace("%COUNTDOWN%", str(countdown)).replace("%SHOTS%", str(shots))
    st.components.v1.html(capture_code, height=0, width=0)

    # Receive images
    images_data = st.experimental_get_query_params().get("streamlit-webcam")
    if images_data:
        st.success("Photos captured! Combining strip…")
        # Decode and combine images
        pil_images = []
        for idx, img_b64 in enumerate(images_data):
            img_bytes = base64.b64decode(img_b64.split(",")[1])
            img = Image.open(io.BytesIO(img_bytes))
            pil_images.append(img)

        # Create strip
        widths, heights = zip(*(i.size for i in pil_images))
        total_h = sum(heights)
        max_w = max(widths)
        strip = Image.new("RGB", (max_w, total_h))
        y_offset = 0
        for im in pil_images:
            strip.paste(im, (0, y_offset))
            y_offset += im.height

        # Save strip
        fname = f"photobooth_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        strip.save(fname)
        st.image(strip, caption="Your Photo Strip")
        with open(fname, "rb") as f:
            st.download_button("📥 Download Photo Strip", f, file_name=fname)