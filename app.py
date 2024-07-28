import streamlit as st
import google.generativeai as gemini
import transformers
import torch

#prompt
constant_prompt = """
Generate a personalized workout, yoga, and diet plan based on the following parameters:
- Name: {name}
- Weight: {weight} kg
- Gender: {gender}
- Age: {age} years
- Height: {height} cm
- Fitness Level: {fitness_level}
- Medical Conditions/Injuries: {medical_conditions}
- Dietary Preferences/Restrictions: {dietary_preferences}
- Sleep Patterns: {sleep_patterns}
- Fitness Experience: {experience}
- Stress Level: {stress_level}
- Goals: {goals}

The plan should include:
1. A detailed workout routine (including yoga) tailored to the fitness level and goals.
2. A diet plan that aligns with dietary preferences and medical conditions.
3. Suggestions for improving sleep and managing stress to enhance overall fitness.
"""



gemini.configure(api_key=st.secrets["api_key"])

st.header("Personalized Fitness and Diet Plan Generator 💪 🧘 🍽️")

tab1, tab2, tab3 = st.tabs(["Generate", "Plan", "Track"])

# Define the constant prompt


def generate_plan(name, weight, gender, age, height, fitness_level, medical_conditions, dietary_preferences, sleep_patterns, experience, stress_level, goals):
    # Replace placeholders in the prompt with user inputs
    prompt = f"""
    Generate a personalized fitness and diet plan based on the following parameters:
    1. **Name** : {name}
    2. **Weight**: {weight} kg
    3. **Gender**: {gender}
    4. **Age**: {age} years
    5. **Height**: {height} cm
    6. **Fitness Level**: {fitness_level} (Beginner, Intermediate, Advanced)
    7. **Medical Conditions/Injuries**: {medical_conditions} (if any)
    8. **Dietary Preferences/Restrictions**: {dietary_preferences} (if any)
    9. **Sleep Patterns**: {sleep_patterns} (average hours per night)
    10. **Fitness Experience**: {experience} (e.g., years of training)
    11. **Stress Level**: {stress_level} (Low, Medium, High)
    12. **Goals**: {goals} (e.g., muscle gain, weight loss)

    **Instructions:**

    1. **Workout Plan**:
    - Provide a detailed weekly workout routine that includes exercises for strength training, cardio, and flexibility.
    - Include recommendations for yoga practices if applicable.
    - Tailor the intensity and volume according to the fitness level and goals.

    2. **Diet Plan**:
    - Create a balanced diet plan that aligns with the dietary preferences and restrictions.
    - Include meal suggestions and portion sizes to meet the nutritional needs and support fitness goals.

    3. **Additional Recommendations**:
    - Suggest strategies for improving sleep quality and managing stress to enhance overall fitness and well-being.

    The plan should be practical and achievable, considering the user’s medical conditions, fitness level, and experience. Ensure that the suggestions are safe and effective for the user’s specific situation.
        """
            
        # Use the llama 3.1 to generate the plan

    model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

    pipeline = transformers.pipeline(
        "text-generation",
        model=model_id,
        model_kwargs={"torch_dtype": torch.bfloat16},
        device_map="auto",
    )

    messages = [
        {"role": "system", "content": "You are a fitness trainer who figure out the workout yoga and diet plans for users."},
        {"role": "user", "content": constant_prompt},
    ]

    print(pipeline(
        messages,
        max_new_tokens=65536,
    ))




# Initialize session state for the plan and progress
if 'plan' not in st.session_state:
    st.session_state.plan = None
if 'progress' not in st.session_state:
    st.session_state.progress = {week: "" for week in range(1, 13)}

with tab1:
    # Collect user inputs for body parameters
    with st.form(key='user_params'):
        name = st.text_input("Name")
        weight = st.number_input("Weight (kg)", min_value=0.0, format="%.2f")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.number_input("Age (years)", min_value=0, format="%d")
        height = st.number_input("Height (cm)", min_value=0, format="%d")
        fitness_level = st.selectbox("Fitness Level", ["Beginner", "Intermediate", "Advanced"])
        medical_conditions = st.text_area("Medical Conditions/Injuries (if any)")
        dietary_preferences = st.text_area("Dietary Preferences/Restrictions (if any)")
        sleep_patterns = st.text_area("Sleep Patterns (average hours per night)")
        experience = st.text_area("Fitness Experience (e.g., years of training)")
        stress_level = st.selectbox("Stress Level", ["Low", "Medium", "High"])
        goals = st.text_area("Fitness Goals (e.g., muscle gain, weight loss)")
        
        submit_button = st.form_submit_button("Generate Plan")

    # Display generated plan if the form is submitted
    if submit_button:
        with st.spinner("Generating your personalized plan..."):
            plan = generate_plan(name, weight, gender, age, height, fitness_level, medical_conditions, dietary_preferences, sleep_patterns, experience, stress_level, goals)
            st.session_state.plan = plan
            st.write("Please see your plan in the Plan tab.")

with tab2:
    st.write("Your Personalized Fitness Plan")
    if st.session_state.plan:
        st.write(st.session_state.plan)
    else:
        st.write("No plan generated yet. Please go to the Generate tab to create your plan.")

with tab3:
    with tab3:
        st.write("Track your Progress")
        
        # Iterate through weeks 1 to 12
        for week in range(1, 13):
            st.subheader(f"Week {week}")
            workout_completion = st.radio(f"Did you complete the workout plan in week {week}?", ["Yes", "No"])
            diet_completion = st.radio(f"Did you complete the diet plan in week {week}?", ["Yes", "No"])
            
            # Store completion status in session state
            if workout_completion == "Yes" and diet_completion == "Yes":
                st.session_state.progress[week] = "Completed"
            else:
                st.session_state.progress[week] = "Not Completed"
        
        st.write("Overall Progress:")
        for week, progress in st.session_state.progress.items():
            st.write(f"Week {week}: {progress}")

        if all(progress == "Completed" for progress in st.session_state.progress.values()):
            # All weeks completed, generate plan for next 12 weeks
            st.write("Congratulations! You have completed all 12 weeks.")
            
            # Allow user to input any adjustments or goals for the next 12 weeks
            st.subheader("Plan for Next 12 Weeks")
            adjustments = st.text_area("Any adjustments or new goals for the next 12 weeks?")
            
            # Use the previously generated plan from the Generate tab
            if st.session_state.plan:
                previous_plan = st.session_state.plan
                prompt_next_12_weeks = f"Generate a personalized fitness and diet plan for the next 12 weeks incorporating the following progress:\n{previous_plan}\n\nAdjustments/Goals:\n{adjustments}"
                
                # Use Gemini API to generate the plan for next 12 weeks
                if st.button("Generate Plan for Next 12 Weeks"):
                    model = gemini.GenerativeModel('gemini-1.5-flash')
                    next_12_weeks_plan = model.generate_content(prompt_next_12_weeks)
                    st.write("Plan for Next 12 Weeks:")
                    st.write(next_12_weeks_plan.text)
            else:
                st.write("No plan generated yet. Please go to the Generate tab to create your plan.")
        else:
            st.write("Keep going! Complete all weeks to generate the plan for the next 12 weeks.")


