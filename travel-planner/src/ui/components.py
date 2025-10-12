"""Reusable UI components"""

import streamlit as st
from datetime import date, timedelta
from typing import Optional
from src.models import UserInput


def render_input_form() -> Optional[UserInput]:
    """
    Render input form for trip details
    
    Returns:
        UserInput model if valid, None otherwise
    """
    st.header("📝 Trip Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        destination = st.text_input(
            "Destination",
            placeholder="e.g., Paris, France",
            help="Enter your destination city or country"
        )
        
        start_date = st.date_input(
            "Start Date",
            value=date.today() + timedelta(days=30),
            min_value=date.today(),
            help="When does your trip begin?"
        )
        
        end_date = st.date_input(
            "End Date",
            value=date.today() + timedelta(days=33),
            min_value=date.today(),
            help="When does your trip end?"
        )
    
    with col2:
        budget_min = st.number_input(
            "Minimum Budget ($)",
            min_value=0,
            value=1500,
            step=100,
            help="Minimum budget for your trip"
        )
        
        budget_max = st.number_input(
            "Maximum Budget ($)",
            min_value=0,
            value=3000,
            step=100,
            help="Maximum budget for your trip"
        )
    
    # Preferences
    st.subheader("Preferences")
    
    col3, col4 = st.columns(2)
    
    with col3:
        pace = st.selectbox(
            "Travel Pace",
            ["Relaxed", "Moderate", "Packed"],
            index=1,
            help="How many activities per day?"
        )
        
        food_prefs = st.multiselect(
            "Food Preferences",
            ["Italian", "French", "Asian", "Mexican", "Mediterranean", 
             "Vegetarian", "Vegan", "Local Cuisine"],
            help="Select your food preferences"
        )
    
    with col4:
        activities = st.multiselect(
            "Activity Types",
            ["Cultural", "Adventure", "Relaxation", "Nightlife", 
             "Shopping", "Nature", "Food & Wine", "History"],
            help="What types of activities interest you?"
        )
        
        content_filter = st.radio(
            "Content Filter",
            ["Family-Friendly", "Adults-Only"],
            horizontal=True,
            help="Filter recommendations based on audience"
        )
    
    # Validation
    if not destination:
        return None
    
    if start_date >= end_date:
        st.error("End date must be after start date")
        return None
    
    if budget_min >= budget_max:
        st.error("Maximum budget must be greater than minimum budget")
        return None
    
    # Create UserInput model
    try:
        user_input = UserInput(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget_range=(budget_min, budget_max),
            pace=pace.lower(),
            food_preferences=food_prefs,
            activities=activities,
            content_filter=content_filter.lower().replace("-", "_")
        )
        return user_input
    except Exception as e:
        st.error(f"Input validation error: {e}")
        return None


def render_section_buttons():
    """
    Render navigation buttons for plan sections
    
    NOTE: These buttons ONLY switch views - NO agent calls!
    All data is loaded from st.session_state.travel_plan
    
    Returns:
        Selected section key
    """
    # Initialize session state for selected section
    if 'selected_section' not in st.session_state:
        st.session_state.selected_section = 'places_to_stay'
    
    st.markdown("### 📑 Plan Sections")
    st.caption("✅ All data cached - clicking buttons just switches views (no agent calls)")
    
    # Create 4 columns for buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(
            "🏨 Places to Stay",
            use_container_width=True,
            type="primary" if st.session_state.selected_section == 'places_to_stay' else "secondary",
            key="btn_places"
        ):
            st.session_state.selected_section = 'places_to_stay'
            st.rerun()
    
    with col2:
        if st.button(
            "🎭 Activities",
            use_container_width=True,
            type="primary" if st.session_state.selected_section == 'activities' else "secondary",
            key="btn_activities"
        ):
            st.session_state.selected_section = 'activities'
            st.rerun()
    
    with col3:
        if st.button(
            "🚗 Transportation",
            use_container_width=True,
            type="primary" if st.session_state.selected_section == 'transportation' else "secondary",
            key="btn_transport"
        ):
            st.session_state.selected_section = 'transportation'
            st.rerun()
    
    with col4:
        if st.button(
            "📅 Itinerary",
            use_container_width=True,
            type="primary" if st.session_state.selected_section == 'itinerary' else "secondary",
            key="btn_itinerary"
        ):
            st.session_state.selected_section = 'itinerary'
            st.rerun()
    
    return st.session_state.selected_section


def render_section_content(plan, section_key: str):
    """
    Render content for selected section
    
    Args:
        plan: TravelPlan object
        section_key: Section to display
    """
    st.markdown("---")
    
    section_map = {
        'places_to_stay': ('🏨 Places to Stay', plan.places_to_stay),
        'activities': ('🎭 Activities', plan.activities),
        'transportation': ('🚗 Transportation', plan.transportation),
        'itinerary': ('📅 Day-by-Day Itinerary', plan.itinerary)
    }
    
    if section_key in section_map:
        title, content = section_map[section_key]
        st.header(title)
        st.markdown(content)


def render_progress(message: str = "Planning your trip..."):
    """
    Render progress indicator
    
    Args:
        message: Progress message to display
    """
    with st.spinner(message):
        st.empty()


def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
        <style>
        /* Main title styling */
        h1 {
            color: #1E88E5;
            font-weight: 700;
        }
        
        /* Section headers */
        h2 {
            color: #424242;
            margin-top: 1.5rem;
        }
        
        /* Button styling */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        /* Primary button (selected) */
        .stButton>button[kind="primary"] {
            background-color: #1E88E5;
            border: 2px solid #1E88E5;
        }
        
        /* Secondary button (not selected) */
        .stButton>button[kind="secondary"] {
            background-color: #f0f0f0;
            color: #424242;
            border: 2px solid #e0e0e0;
        }
        
        /* Hover effect */
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* Container padding */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Markdown content */
        .markdown-text-container {
            font-size: 1rem;
            line-height: 1.6;
        }
        </style>
    """, unsafe_allow_html=True)

