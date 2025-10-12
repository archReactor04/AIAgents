"""Main Streamlit application"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from swarm import Swarm
from src.utils.config import Config
from src.models import TravelPlan
from src.ui.components import (
    render_input_form,
    render_section_buttons,
    render_section_content,
    apply_custom_css
)
from src.agents import (
    create_supervisor_agent,
    create_research_agent,
    create_budget_agent,
    create_itinerary_agent,
    create_recommendation_agent
)


# Page configuration
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_app():
    """Initialize application and validate configuration"""
    try:
        Config.validate()
        return True
    except ValueError as e:
        st.error(f"⚠️ Configuration Error: {e}")
        st.info("""
        **How to fix:**
        1. Create a `.env` file in the project root
        2. Add your OpenAI API key: `OPENAI_API_KEY=your_openai_key`
        4. Restart the app
        """)
        return False


def parse_plan_sections(plan_text: str) -> TravelPlan:
    """
    Parse supervisor's output into structured sections
    
    Args:
        plan_text: Raw text from supervisor
    
    Returns:
        TravelPlan object with sections and images
    """
    import streamlit as st
    
    # Split by section headers
    sections = {
        'places_to_stay': '',
        'activities': '',
        'transportation': '',
        'itinerary': ''
    }
    
    # DEBUG: Show parsing process
    with st.expander("🔍 Debug: Parsing Process", expanded=False):
        st.write("**Looking for section markers in the text...**")
        
        # Strategy 1: Look for explicit section markers
        import re
        
        # Pattern: === SECTION START: NAME === content === SECTION END: NAME ===
        patterns = {
            'places_to_stay': r'===\s*SECTION START:\s*PLACES TO STAY\s*===\s*(.+?)\s*===\s*SECTION END:\s*PLACES TO STAY\s*===',
            'activities': r'===\s*SECTION START:\s*ACTIVITIES\s*===\s*(.+?)\s*===\s*SECTION END:\s*ACTIVITIES\s*===',
            'transportation': r'===\s*SECTION START:\s*TRANSPORTATION\s*===\s*(.+?)\s*===\s*SECTION END:\s*TRANSPORTATION\s*===',
            'itinerary': r'===\s*SECTION START:\s*ITINERARY\s*===\s*(.+?)\s*===\s*SECTION END:\s*ITINERARY\s*==='
        }
        
        sections_found = []
        for section_key, pattern in patterns.items():
            match = re.search(pattern, plan_text, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section_key] = match.group(1).strip()
                sections_found.append(section_key)
                st.write(f"✅ Found section: {section_key} ({len(sections[section_key])} characters)")
            else:
                st.write(f"❌ Missing section: {section_key}")
        
        # Fallback: If structured markers not found, try old parsing method
        if len(sections_found) == 0:
            st.warning("⚠️ Structured markers not found, trying fallback parsing...")
            
            lines = plan_text.split('\n')
            current_section = None
            current_content = []
            
            for line_num, line in enumerate(lines):
                line_lower = line.lower()
                
                # Detect section headers (look for emoji or text)
                if ('places to stay' in line_lower or '🏨' in line):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'places_to_stay'
                    current_content = []
                elif ('activities' in line_lower or '🎭' in line) and 'day-by-day' not in line_lower and 'itinerary' not in line_lower:
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'activities'
                    current_content = []
                elif ('transportation' in line_lower or '🚗' in line):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'transportation'
                    current_content = []
                elif ('itinerary' in line_lower or '📅' in line or 'day-by-day' in line_lower):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'itinerary'
                    current_content = []
                elif line.strip() == '---':
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                        current_content = []
                elif line.strip().startswith('#'):
                    continue
                else:
                    if current_section:
                        current_content.append(line)
            
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
        
        st.write(f"\n**Final section lengths:**")
        for key, content in sections.items():
            st.write(f"- {key}: {len(content)} characters")
    
    # Fallback: if parsing failed, put everything in itinerary
    if not any([sections['places_to_stay'], sections['activities'], sections['transportation'], sections['itinerary']]):
        st.warning("⚠️ Parsing failed - no sections found! Using fallback.")
        sections['itinerary'] = plan_text
        sections['places_to_stay'] = "⚠️ Parsing error - check debug output"
        sections['activities'] = "⚠️ Parsing error - check debug output"
        sections['transportation'] = "⚠️ Parsing error - check debug output"
    
    return TravelPlan(**sections)


def create_travel_plan(user_input):
    """
    Execute travel planning with agents - RUNS ONCE to gather all data
    
    Args:
        user_input: UserInput model
    
    Returns:
        TravelPlan object or None if failed
    """
    try:
        # Initialize Swarm client
        client = Swarm()
        
        # Create all agents upfront
        supervisor = create_supervisor_agent()
        research = create_research_agent()
        budget = create_budget_agent()
        itinerary = create_itinerary_agent()
        recommendation = create_recommendation_agent()
        
        # Prepare comprehensive context for agents
        context_message = f"""
Create a COMPLETE travel plan. Follow these steps EXACTLY:

STEP 1: Call Research Agent
STEP 2: Call Budget Agent  
STEP 3: Call Itinerary Agent
STEP 4: Call Recommendation Agent
STEP 5: Create final plan using ALL the information gathered

{user_input.to_prompt_context()}

FINAL OUTPUT MUST HAVE EXACTLY 4 SECTIONS WITH THESE EXACT HEADERS:

=== SECTION START: PLACES TO STAY ===
[Write 3-5 hotel recommendations here with names, prices, locations]
=== SECTION END: PLACES TO STAY ===

=== SECTION START: ACTIVITIES ===
[Write 8-12 specific attraction/activity recommendations here - NO day numbers, just a list!]
Examples: "Eiffel Tower", "Louvre Museum", "Seine River Cruise", etc.
=== SECTION END: ACTIVITIES ===

=== SECTION START: TRANSPORTATION ===
[Write complete transportation guide here]
MUST include: Airport names with codes (e.g., "JFK", "CDG"), how to get from airport to city, local transport options with costs
=== SECTION END: TRANSPORTATION ===

=== SECTION START: ITINERARY ===
[Write complete day-by-day schedule for ALL days here]
Day 1: [morning, afternoon, evening]
Day 2: [morning, afternoon, evening]
[etc. for ALL days]
=== SECTION END: ITINERARY ===

⚠️ CRITICAL: DO NOT SKIP ANY SECTION! Each section MUST have real content!
⚠️ Use EXACT section markers: "=== SECTION START: [NAME] ===" and "=== SECTION END: [NAME] ==="
⚠️ Apply {user_input.content_filter} filter
⚠️ Budget: ${user_input.budget_range[0]:,.0f}-${user_input.budget_range[1]:,.0f}
"""
        
        # Run Swarm orchestration with progress updates
        with st.spinner("🤖 AI agents are planning your trip..."):
            # Create progress placeholder
            progress_text = st.empty()
            status_text = st.empty()
            
            progress_text.text("✨ Coordinating AI agents...")
            status_text.info("📋 This will take 20-40 seconds. All data is gathered once, then you can navigate seamlessly.")
            
            # Execute with supervisor - ALL agents run here
            response = client.run(
                agent=supervisor,
                messages=[{"role": "user", "content": context_message}],
                max_turns=Config.MAX_TURNS,
                context_variables={
                    "research_agent": research,
                    "budget_agent": budget,
                    "itinerary_agent": itinerary,
                    "recommendation_agent": recommendation
                }
            )
            
            progress_text.empty()
            status_text.empty()
        
        # Extract final plan from response
        if response and response.messages:
            final_message = response.messages[-1]["content"]
            
            # DEBUG: Show ALL messages to see agent interactions
            with st.expander("🔍 Debug: View ALL Agent Messages", expanded=True):
                st.write(f"**Total messages in conversation: {len(response.messages)}**")
                st.write("---")
                for idx, msg in enumerate(response.messages):
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    sender = msg.get("sender", "unknown")
                    
                    st.write(f"**Message {idx + 1}** - Role: `{role}` - Sender: `{sender}`")
                    with st.expander(f"Message {idx + 1} Content", expanded=(idx == len(response.messages) - 1)):
                        st.code(content[:2000] + ("..." if len(content) > 2000 else ""), language="markdown")
                    st.write("---")
            
            # Parse into sections
            plan = parse_plan_sections(final_message)
            
            # Validate that sections have content
            empty_sections = []
            if not plan.places_to_stay or len(plan.places_to_stay.strip()) < 50:
                empty_sections.append("Places to Stay")
            
            if not plan.activities or len(plan.activities.strip()) < 50:
                empty_sections.append("Activities")
            
            if not plan.transportation or len(plan.transportation.strip()) < 50:
                empty_sections.append("Transportation")
            
            if not plan.itinerary or len(plan.itinerary.strip()) < 50:
                empty_sections.append("Itinerary")
            
            if empty_sections:
                st.error(f"⚠️ Empty sections detected: {', '.join(empty_sections)}")
                st.error("The supervisor did not follow instructions properly. Check the debug output above.")
            
            return plan
        else:
            st.error("No response received from agents")
            return None
            
    except Exception as e:
        st.error(f"Error generating travel plan: {e}")
        st.exception(e)
        return None


def main():
    """Main application"""
    
    # Apply custom styling
    apply_custom_css()
    
    # Check configuration
    if not initialize_app():
        st.stop()
    
    # Initialize session state
    if 'plan_generated' not in st.session_state:
        st.session_state.plan_generated = False
    if 'travel_plan' not in st.session_state:
        st.session_state.travel_plan = None
    if 'selected_section' not in st.session_state:
        st.session_state.selected_section = 'places_to_stay'
    if 'generation_in_progress' not in st.session_state:
        st.session_state.generation_in_progress = False
    
    # Header
    st.title("🌍 AI-Powered Travel Planner")
    st.markdown("""
    Plan your perfect trip with AI agents that research destinations, 
    manage budgets, create itineraries, and provide personalized recommendations.
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        st.info(f"**Model:** {Config.OPENAI_MODEL}")
        st.info("**Agents:** 5 specialized agents")
        st.info("**Knowledge:** Built-in GPT knowledge")
        
        st.markdown("---")
        
        st.subheader("📊 Status")
        if st.session_state.plan_generated:
            st.success("✅ Plan ready")
            st.info("🔒 Navigation locked (no re-execution)")
        else:
            st.info("📝 Waiting for input")
        
        st.markdown("---")
        
        st.subheader("📊 Cache")
        from src.utils.cache import search_cache
        st.metric("Cached items", search_cache.size())
        
        if st.button("Clear Cache", use_container_width=True):
            search_cache.clear()
            st.success("Cache cleared!")
            st.rerun()
        
        st.markdown("---")
        st.caption("Built with OpenAI Swarm")
    
    # Show input form ONLY if no plan is generated
    if not st.session_state.plan_generated:
        # Input form
        user_input = render_input_form()
        
        # Generate button
        st.markdown("---")
        
        if st.button("🚀 Generate Travel Plan", type="primary", use_container_width=True, key="generate_btn"):
            if user_input is None:
                st.error("Please fill in all required fields correctly")
            else:
                # Mark generation in progress
                st.session_state.generation_in_progress = True
                
                # Execute travel planning (ONLY HAPPENS ONCE HERE!)
                plan = create_travel_plan(user_input)
                
                if plan:
                    # Store plan in session state
                    st.session_state.travel_plan = plan
                    st.session_state.plan_generated = True
                    st.session_state.generation_in_progress = False
                    st.success("✅ Travel plan generated successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.session_state.generation_in_progress = False
    
    # Display plan if generated (ISOLATED FROM GENERATION LOGIC!)
    elif st.session_state.plan_generated and st.session_state.travel_plan:
        st.markdown("---")
        
        # Header with "Start New Plan" button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("## 📋 Your Travel Plan")
        with col2:
            if st.button("🔄 Start New Plan", type="primary", use_container_width=True, key="start_new_main"):
                st.session_state.plan_generated = False
                st.session_state.travel_plan = None
                st.session_state.selected_section = 'places_to_stay'
                st.rerun()
        
        st.info("🔒 All data is cached! Clicking buttons below ONLY switches views - no agents are called.")
        
        plan = st.session_state.travel_plan
        
        # Section navigation buttons (ONLY switches display, guaranteed no agent calls!)
        selected_section = render_section_buttons()
        
        # Display selected section from cached data (ONLY reads from session state!)
        render_section_content(plan, selected_section)
        
        # Download button
        st.markdown("---")
        st.download_button(
            label="📥 Download Full Plan (Markdown)",
            data=plan.to_markdown(),
            file_name=f"travel_plan_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True
        )


if __name__ == "__main__":
    main()

