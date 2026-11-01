"""
RentLens AI - Practical Safety Inspection Checklist View.
Equips prospective renters with a rigorous, categorized pre-move-in checklist
covering electrical, plumbing, ventilation, pests, moisture, security, and fire safety.
"""

import streamlit as st
from components.cards import render_section_header, render_kpi_card

CHECKLIST_ITEMS = {
    "Electrical Safety": [
        ("elec_1", "All wall switch plates and outlet covers are present, secure, and free of cracks."),
        ("elec_2", "Kitchen and bathroom outlets feature functional GFCI buttons that trip and reset."),
        ("elec_3", "No exposed, frayed, or uninsulated wiring is visible in living spaces, closets, or basements."),
        ("elec_4", "Main electrical breaker panel is accessible, fully labeled, and not showing scorched fuses.")
    ],
    "Plumbing & Water Flow": [
        ("plumb_1", "Hot and cold water faucets run at adequate pressure simultaneously in kitchen and bath."),
        ("plumb_2", "No active dripping or moisture detected on supply lines or P-traps underneath sinks."),
        ("plumb_3", "Drains empty swiftly without bubbling, gurgling noises, or standing water pools."),
        ("plumb_4", "Toilets flush cleanly and fill shutoff valve stops running completely after refill.")
    ],
    "Ventilation & Air Quality": [
        ("vent_1", "Bathroom exhaust fans run properly and hold a sheet of toilet paper to the grill by suction."),
        ("vent_2", "Kitchen range hood operates and exhausts externally or through clean charcoal filters."),
        ("vent_3", "No lingering musty, chemical, or sewer gas odors detected upon entering closed rooms."),
        ("vent_4", "HVAC return air filter is clean and properly seated without heavy dust or pet fur buildup.")
    ],
    "Pests & Rodents": [
        ("pest_1", "Kitchen cabinetry, pantry shelves, and under-sink bases are clean of rodent droppings or insect frass."),
        ("pest_2", "Spaces behind refrigerator and stove do not contain sticky traps or cockroach egg casings."),
        ("pest_3", "Plumbing pipe penetrations through drywall have tight escutcheon plates with no gaps.")
    ],
    "Water Damage & Mold": [
        ("water_1", "Ceilings beneath bathrooms and upper levels have zero water rings, stains, or sagging plaster."),
        ("water_2", "Bathroom floor tiles and baseboards around tub/shower are firm and show no sponginess."),
        ("water_3", "Shower silicone caulking and tile grout are intact with no persistent black mold growth."),
        ("water_4", "Window sills and lower wall corners are free of bubbling, peeling paint or condensation rot.")
    ],
    "Locks & Physical Security": [
        ("sec_1", "Exterior entry doors have a functional deadbolt that extends at least 1 inch into the jamb."),
        ("sec_2", "All ground-floor windows and fire escapes latch and lock tightly from the inside."),
        ("sec_3", "Main entry door features an unobstructed peephole or security camera viewer.")
    ],
    "Fire & Life Safety": [
        ("fire_1", "Certified smoke alarms are installed on each level and directly outside all sleeping rooms."),
        ("fire_2", "Carbon monoxide alarms are present if the property has gas appliances or an attached garage."),
        ("fire_3", "Test button on smoke alarms triggers a loud, continuous alarm siren."),
        ("fire_4", "Bedroom windows open smoothly and provide an unobstructed secondary emergency egress.")
    ]
}


def render_checklist_page():
    """Renders the interactive physical rental inspection checklist."""
    render_section_header(
        title="Physical Rental Safety Checklist",
        subtitle="Step-by-step room walkthrough guide. Check off items during your in-person showing before handing over funds.",
        icon="✅"
    )

    # Initialize state for all checklist items
    total_items = sum(len(items) for items in CHECKLIST_ITEMS.values())
    checked_count = 0

    if "checklist_state" not in st.session_state:
        st.session_state.checklist_state = {}

    for cat, items in CHECKLIST_ITEMS.items():
        for key, text in items:
            if key not in st.session_state.checklist_state:
                st.session_state.checklist_state[key] = False
            if st.session_state.checklist_state[key]:
                checked_count += 1

    completion_pct = int((checked_count / total_items) * 100) if total_items > 0 else 0

    # Progress Summary Bar
    prog_col1, prog_col2 = st.columns([3, 1])
    with prog_col1:
        st.progress(completion_pct / 100.0, text=f"Walkthrough Verification Progress: {checked_count} of {total_items} items confirmed ({completion_pct}%)")
    with prog_col2:
        if completion_pct >= 90:
            badge_text = "MOVE-IN READY"
            badge_class = "low"
        elif completion_pct >= 60:
            badge_text = "ADDENDUM NEEDED"
            badge_class = "medium"
        else:
            badge_text = "INCOMPLETE WALKTHROUGH"
            badge_class = "high"
        st.markdown(f"<div style='text-align: right; margin-top: 0.5rem;'><span class='rl-badge rl-badge-{badge_class}'>{badge_text}</span></div>", unsafe_allow_html=True)

    st.markdown("<hr style='margin: 1.25rem 0;' />", unsafe_allow_html=True)

    # Render Categories in 2 balanced columns
    cat_names = list(CHECKLIST_ITEMS.keys())
    col_left, col_right = st.columns(2)

    for idx, cat in enumerate(cat_names):
        col = col_left if idx % 2 == 0 else col_right
        with col:
            st.markdown(
                f"""
                <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.2rem; margin-bottom: 1.25rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);">
                    <div style="font-weight: 700; font-size: 1.05rem; color: #1F4E46; margin-bottom: 0.6rem; border-bottom: 1px solid #F1F5F9; padding-bottom: 0.4rem;">
                        {cat}
                    </div>
                """,
                unsafe_allow_html=True
            )

            for key, text in CHECKLIST_ITEMS[cat]:
                is_checked = st.checkbox(
                    text,
                    value=st.session_state.checklist_state.get(key, False),
                    key=f"chk_{key}"
                )
                st.session_state.checklist_state[key] = is_checked

            st.markdown("</div>", unsafe_allow_html=True)

    # Actions & Export
    st.markdown("<h2>Checklist Summary & Export</h2>", unsafe_allow_html=True)
    
    act_col1, act_col2 = st.columns([2, 1])
    with act_col1:
        # Build text summary for tenant records or emailing landlord
        summary_lines = [
            f"RENTLENS AI - IN-PERSON RENTAL SAFETY CHECKLIST SUMMARY",
            f"Verified Items: {checked_count} / {total_items} ({completion_pct}%)\n",
            "=" * 60
        ]
        
        unchecked_by_cat = {}
        for cat, items in CHECKLIST_ITEMS.items():
            missing = [text for key, text in items if not st.session_state.checklist_state.get(key, False)]
            if missing:
                unchecked_by_cat[cat] = missing

        if unchecked_by_cat:
            summary_lines.append("\nITEMS FLAGGED FOR LANDLORD ATTENTION / REPAIR BEFORE MOVE-IN:")
            for cat, items in unchecked_by_cat.items():
                summary_lines.append(f"\n[{cat}]")
                for it in items:
                    summary_lines.append(f"  [ ] {it}")
        else:
            summary_lines.append("\nALL STANDARD SAFETY & HABITABILITY ITEMS CONFIRMED OK.")

        summary_text = "\n".join(summary_lines)

        st.download_button(
            label="📥 Download Checklist Notes (.txt)",
            data=summary_text,
            file_name="RentLens_Safety_Checklist.txt",
            mime="text/plain",
            use_container_width=True
        )

    with act_col2:
        if st.button("🔄 Reset Checklist", use_container_width=True):
            for k in st.session_state.checklist_state:
                st.session_state.checklist_state[k] = False
            st.rerun()
