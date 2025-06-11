# Crop Health Estimator for Agriculture - Python with Interactive SiliconFlow LLM and Typing Effect
from datetime import datetime
import os
import requests
import json
import time
import sys

# SiliconFlow API configuration - REPLACE 'your-api-key-here' with your actual key
API_KEY = "MyKey"  # Get this from SiliconFlow dashboard
API_URL = "https://api.siliconflow.cn/v1/completions"  # Check SiliconFlow docs for exact endpoint
MODEL = "Qwen/Qwen2-7B-Instruct"  # Example model; update based on SiliconFlow's offerings

print("Welcome to the Crop Health Estimator!")

# Function to simulate typing effect
def type_effect(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # New line after typing

# Function to get valid input
def get_valid_input(prompt, min_val, max_val):
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                print("Input cannot be empty. Please try again.")
                continue
            value = float(value)
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Please enter a value between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input! Please enter a number.")
        except EOFError:
            print("Unexpected end of input. Please try again.")

# Function to get crop type
def get_crop_type():
    crops = {
        1: ("Wheat", 40, (10, 25), 5, (80, 20)),
        2: ("Corn", 50, (20, 35), 5, (85, 30)),
        3: ("Rice", 70, (25, 35), 6, (90, 28))
    }
    while True:
        try:
            print("\nChoose a crop type:")
            for key, (name, _, _, _, _) in crops.items():
                print(f"{key}. {name}")
            choice = input("Enter number (1-3): ").strip()
            if not choice:
                print("Input cannot be empty. Please try again.")
                continue
            choice = int(float(choice))
            if choice in crops:
                return crops[choice]
            else:
                print("Please enter a number between 1 and 3.")
        except ValueError:
            print("Invalid input! Please enter a number.")
        except EOFError:
            print("Unexpected end of input. Please try again.")

# Collect multiple field readings with location
def collect_readings():
    readings = []
    while True:
        try:
            num_fields = input("How many fields to assess (1-10)? ").strip()
            if not num_fields:
                print("Input cannot be empty. Please try again.")
                continue
            num_fields = int(float(num_fields))
            if 1 <= num_fields <= 10:
                break
            else:
                print("Please enter a value between 1 and 10.")
        except ValueError:
            print("Invalid input! Please enter a number.")
        except EOFError:
            print("Unexpected end of input. Please try again.")
    
    for i in range(num_fields):
        print(f"\nField {i+1} Data:")
        field_name = input("Enter field name (e.g., North Field) or press Enter for default: ").strip() or f"Field {i+1}"
        soil_moisture = get_valid_input("Enter soil moisture level (0-100%): ", 0, 100)
        temperature = get_valid_input("Enter average temperature (in Celsius, -50 to 50): ", -50, 50)
        veg_score = get_valid_input("Enter vegetation score (0-10, from remote sensing): ", 0, 10)
        location = input("Enter field location (e.g., 'West Farm') or press Enter for default: ").strip() or "Unknown"
        readings.append({"field": field_name, "location": location, "moisture": soil_moisture, "temp": temperature, "veg": veg_score})
    return readings

# Assess health with AI-like logic
def assess_health(moisture, temp, veg, crop_data):
    crop, moisture_min, temp_range, veg_min, disease_risk = crop_data
    moisture_score = (moisture / 100) * 35  # 35% weight
    temp_score = 0
    if temp_range[0] <= temp <= temp_range[1]:
        temp_score = 30  # 30% weight
    else:
        temp_diff = min(abs(temp - temp_range[0]), abs(temp - temp_range[1]))
        temp_score = max(0, 30 - temp_diff * 2)
    veg_score_scaled = veg * 3.5  # 35% weight
    health_score = moisture_score + temp_score + veg_score_scaled
    risk = "Low"
    if moisture > disease_risk[0] and temp > disease_risk[1]:
        risk = "High - Risk of fungal disease! Act fast."
    elif moisture > disease_risk[0] - 10 or temp > disease_risk[1] - 5:
        risk = "Moderate - Monitor for pests or rot."
    if health_score >= 80:
        health = "Excellent"
        tip = "Perfect conditions! Crops thriving."
    elif health_score >= 60:
        health = "Good"
        tip = "Solid growth! Monitor for improvements."
    elif health_score >= 40:
        health = "Fair"
        tip = "Needs work. Check soil, temp, or vegetation."
    else:
        health = "Poor"
        tip = "Urgent! "
        if moisture < moisture_min:
            tip += f"Add water for {crop}."
        elif temp < temp_range[0] or temp > temp_range[1]:
            tip += f"Adjust temperature for {crop}."
        else:
            tip += f"Boost vegetation for {crop}."
    return health_score, health, tip, risk

# Trend analysis with predictive insight
def analyze_trends(readings, crop_data):
    if not readings:
        return "No data to analyze."
    crop = crop_data[0]
    total_score = 0
    excellent = good = fair = poor = 0
    high_risk = 0
    for r in readings:
        score, health, _, risk = assess_health(r["moisture"], r["temp"], r["veg"], crop_data)
        total_score += score
        if health == "Excellent":
            excellent += 1
        elif health == "Good":
            good += 1
        elif health == "Fair":
            fair += 1
        else:
            poor += 1
        if "High" in risk:
            high_risk += 1
    avg_score = total_score / len(readings)
    trend = f"Average Health Score: {avg_score:.1f}/100\n"
    trend += f"Fields: {excellent} Excellent, {good} Good, {fair} Fair, {poor} Poor\n"
    prediction = "Prediction: "
    if high_risk > len(readings) / 2:
        trend += "Alert: High disease risk in many fields! Act fast.\n"
        prediction += "Disease outbreak likely soon—apply fungicides, improve drainage."
    elif avg_score < 60:
        trend += "Warning: Low overall health. Review remote sensing data.\n"
        prediction += "Crop yield may drop—adjust water or temp soon."
    else:
        trend += "Trend: Most fields stable. Keep monitoring!\n"
        prediction += "Stable growth expected—continue current practices."
    return trend + prediction

# Query SiliconFlow LLM
def query_llm(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "max_tokens": 200,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["text"].strip()
        else:
            return "Error: No response from LLM. Check API key or model."
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to SiliconFlow API - {e}"

# Initial LLM advice
def get_initial_llm_advice(crop_name, results, trend_result):
    prompt = f"I’m assessing crop health for {crop_name} using remote sensing data. Here are my results:\n"
    for r in results:
        prompt += f"Field: {r['field']}, Location: {r['location']}, Moisture: {r['moisture']}%, Temperature: {r['temp']}°C, "
        prompt += f"Vegetation Score: {r['veg']}, Health Score: {r['score']:.1f}, Health: {r['health']}, "
        prompt += f"Tip: {r['tip']}, Disease Risk: {r['risk']}\n"
    prompt += f"Trend Analysis: {trend_result}\n"
    prompt += "Based on this, provide specific advice for improving crop health and managing risks."
    advice = query_llm(prompt)
    return advice

# Interactive LLM Q&A with typing effect
def interactive_qa(crop_name, results, trend_result):
    conversation = []
    context = f"Context: Crop health assessment for {crop_name}. Results:\n"
    for r in results:
        context += f"Field: {r['field']}, Moisture: {r['moisture']}%, Temp: {r['temp']}°C, Veg: {r['veg']}, "
        context += f"Score: {r['score']:.1f}, Health: {r['health']}, Risk: {r['risk']}\n"
    context += f"Trend: {trend_result}\n"
    
    print("\n=== Interactive Q&A with LLM ===")
    print("Ask any question about your crops or results (type 'exit' to stop).")
    
    while True:
        try:
            question = input("\nYour question: ").strip()
            if question.lower() == 'exit':
                break
            if not question:
                print("Please enter a question.")
                continue
            
            # Build prompt with context and conversation history
            prompt = context
            if conversation:
                prompt += "Conversation history:\n"
                for q, a in conversation[-3:]:  # Limit to last 3 exchanges
                    prompt += f"Q: {q}\nA: {a}\n"
            prompt += f"Q: {question}\nA: "
            
            answer = query_llm(prompt)
            print("Answer: ", end="")
            type_effect(answer, delay=0.03)  # Typing effect for Q&A
            conversation.append((question, answer))
            
        except EOFError:
            print("Unexpected end of input. Exiting Q&A.")
            break
    
    return conversation

# Main program
try:
    crop_data = get_crop_type()
    crop_name = crop_data[0]
    print(f"\nSelected Crop: {crop_name}")
    readings = collect_readings()

    # Process and display results
    print("\n=== Crop Health Results ===")
    results = []
    for r in readings:
        health_score, health, tip, risk = assess_health(r["moisture"], r["temp"], r["veg"], crop_data)
        results.append({
            "field": r["field"], 
            "location": r["location"], 
            "moisture": r["moisture"],
            "temp": r["temp"], 
            "veg": r["veg"], 
            "score": health_score, 
            "health": health, 
            "tip": tip, 
            "risk": risk
        })
        print(f"Field: {r['field']}")
        print(f"Moisture: {r['moisture']}%, Temperature: {r['temp']}°C, Vegetation: {r['veg']}")
        print(f"Score: {health_score:.1f}/100, Health: {health}, Risk: {risk}")
        print(f"Tip: {tip}\n")

    # Trend analysis and prediction
    print("\n=== Trend Analysis ===")
    trend_result = analyze_trends(readings, crop_data)
    print(trend_result)

    # Initial LLM advice with typing effect
    print("\n=== Initial LLM Crop Advice ===")
    initial_advice = get_initial_llm_advice(crop_name, results, trend_result)
    print("Type:")
    type_effect(initial_advice, delay=0.03)  # Typing effect for initial advice

    # Interactive Q&A
    conversation = interactive_qa(crop_name, results, trend_result)

    # Save results with timestamp, including LLM advice and Q&A
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("CropHealthLog.txt", "a") as file:
        file.write(f"\n=== Assessment on {timestamp} ===\n")
        file.write(f"Crop: {crop_name}\n")
        for r in results:
            file.write(f"Field: {r['field']}, Location: {r['location']}, Moisture: {r['moisture']}%, Temperature: {r['temp']}°C, "
                       f"Vegetation Score: {r['veg']}, Score: {r['score']:.1f}, Health: {r['health']}, "
                       f"Tip: {r['tip']}, Disease Risk: {r['risk']}\n")
        file.write("=== Trend Analysis ===\n")
        file.write(trend_result + "\n")
        file.write("=== Initial LLM Advice ===\n")
        file.write(initial_advice + "\n")
        if conversation:
            file.write("=== Interactive Q&A ===\n")
            for q, a in conversation:
                file.write(f"Q: {q}\nA: {a}\n")
    print("\nResults, trends, LLM advice, and Q&A saved to CropHealthLog.txt!")

    # Action plan
    print("\n=== Action Plan ===")
    print("1. Review CropHealthLog.txt for details.")
    print("2. Update sensor data (moisture, vegetation).")
    print("3. Follow LLM advice and Q&A for crop care.")

except EOFError:
    print("Error: Unexpected end of input. Please restart.")
except Exception as e:
    print(f"An error occurred: {e}. Please restart.")