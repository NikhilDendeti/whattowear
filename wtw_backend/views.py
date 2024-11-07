from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from google.generativeai import GenerativeModel, configure
import json

# Set up the Google Generative AI API key
API_KEY = "AIzaSyAyHB9uJOpdQhFc2HYI4dFLLdRix8km16M"
configure(api_key=API_KEY)


@api_view(['POST'])
def generate_outfit_suggestions(request):
    if request.method == "POST":
        try:
            # Extract data from the request
            wardrobe = request.data.get('wardrobe', {})
            occasion_details = request.data.get('occasion', {})

            # Validate required data
            if not wardrobe or not occasion_details:
                return JsonResponse(
                    {
                        "error": "Both wardrobe and occasion details are required."},
                    status=400
                )

            # Ensure that tops, bottoms, and accessories are lists
            tops = wardrobe.get('tops')
            bottoms = wardrobe.get('bottoms')
            accessories = wardrobe.get('accessories')

            # Convert single items to lists if needed
            if isinstance(tops, str): tops = [tops]
            if isinstance(bottoms, str): bottoms = [bottoms]
            if isinstance(accessories, str): accessories = [accessories]

            # Filter out inappropriate keywords in occasion details
            irrelevant_keywords = [
                "Fuck"
            ]
            occasion_text = " ".join(occasion_details.values()).lower()
            if any(keyword in occasion_text for keyword in
                   irrelevant_keywords):
                return JsonResponse(
                    {"error": "Your input contains inappropriate content."},
                    status=400
                )

            # Construct a prompt for the generative model
            prompt = (
                "You are a fashion assistant. Based on the wardrobe and occasion details provided below, suggest the best outfit combinations.\n\n"
                "Wardrobe:\n"
                f"Tops: {', '.join(tops or [])}\n"
                f"Bottoms: {', '.join(bottoms or [])}\n"
                f"Accessories: {', '.join(accessories or [])}\n\n"
                "Occasion Details:\n"
                f"Occasion: {occasion_details.get('occasion', 'casual')}\n"
                f"Preferred Style: {occasion_details.get('preferred_style', 'stylish and comfortable')}\n"
                f"Going with: {occasion_details.get('whom', 'friends')}\n"
                f"They are wearing: {occasion_details.get('they_wearing', 'casual attire')}\n\n"
                "Suggest suitable outfit combinations and include any style tips. "
                "Respond concisely with an engaging, user-friendly tone."
            )

            # Initialize the model and generate response
            model = GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            # Prepare the JSON response
            outfit_suggestions = response.text.strip() if response and response.text else "No suggestions available."

            return JsonResponse({"suggestions": outfit_suggestions})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            # Log the exception for debugging
            print(f"An error occurred: {e}")
            return JsonResponse(
                {"error": "An internal server error occurred."}, status=500
            )

    return JsonResponse({"error": "Only POST requests are allowed."},
                        status=405)
