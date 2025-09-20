from flask import Flask, request, render_template
import os
from google.cloud import vision
from birdnetlib import analyzer  # Fixed import

# Initialize Flask app
app = Flask(__name__)

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Bird Species Detection/credentials.json"

# Function to detect bird species from images
def detect_bird_species(image_path):
    # Initialize the Vision API client
    client = vision.ImageAnnotatorClient()

    # Load the image
    with open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # Perform object detection
    response = client.object_localization(image=image)

    if response.error.message:
        raise Exception(f"Error in Vision API: {response.error.message}")

    objects = response.localized_object_annotations

    # Log the detected objects for debugging
    print("Detected objects in the image:")
    for obj in objects:
        print(f"Object name: {obj.name}, Confidence: {obj.score}")

    # Improved filtering: Look for objects with high confidence that are birds
    birds = []
    for obj in objects:
        if obj.score > 0.5:  # Filter based on confidence score
            birds.append(obj.name)

    return birds

# Function to detect bird species from audio
def detect_bird_species_audio(audio_path):
    # Initialize the BirdNET analyzer
    analyzer_instance = analyzer.Analyzer()  # Updated initialization

    # Analyze the audio
    results = analyzer_instance.analyze(audio_path)

    # Extract bird species from results
    birds = []
    for result in results:
        birds.append(result["common_name"])

    return birds

# Flask route for the home page
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Handle image upload
        if "image" in request.files:
            image = request.files["image"]
            image_path = os.path.join("uploads", image.filename)
            image.save(image_path)
            print(f"Image saved at: {image_path}")  # Debugging line
            detected_birds = detect_bird_species(image_path)
            return render_template("result.html", birds=detected_birds)

        # Handle audio upload
        elif "audio" in request.files:
            audio = request.files["audio"]
            audio_path = os.path.join("uploads", audio.filename)
            audio.save(audio_path)
            print(f"Audio saved at: {audio_path}")  # Debugging line
            detected_birds = detect_bird_species_audio(audio_path)
            return render_template("result.html", birds=detected_birds)

    return render_template("index.html")

# Run the Flask app
if __name__ == "__main__":
    # Create the uploads folder if it doesn't exist
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    
    app.run(debug=True)
